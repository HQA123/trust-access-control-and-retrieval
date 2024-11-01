package main

import (
	"GoProject/pir"
	"encoding/json"
	"fmt"
	"net"
	"runtime"
)

const LOGQ = uint64(32)
const SEC_PARAM = uint64(1 << 10)

type Message struct {
	Type string
	Data []byte
}

func main() {
	fmt.Println("客户端启动...")

	// PIR scheme initialization
	N := uint64(1 << 22)
	d := uint64(3)
	pi := pir.DoublePIR{}
	p := pi.PickParams(N, d, SEC_PARAM, LOGQ)
	DB := pir.MakeRandomDB(N, d, &p)
	i := []uint64{0}

	//与服务器建立连接
	conn, err := net.Dial("tcp", "127.0.0.1:8000")
	if err != nil {
		fmt.Println("连接服务器失败，err:", err)
		return
	}
	fmt.Println("连接服务器成功...", conn)
	defer conn.Close()

	encoder := json.NewEncoder(conn)
	decoder := json.NewDecoder(conn)

	//接收comp_state和DB.Info
	var comp_state pir.CompressedState
	var offline_download pir.Msg
	for i := 0; i < 3; i++ { // 我们期望接收3条消息
		var msg Message
		err := decoder.Decode(&msg)
		if err != nil {
			fmt.Println("Error decoding message:", err)
			return
		}

		switch msg.Type {
		case "comp_state":
			err = json.Unmarshal(msg.Data, &comp_state)
			if err != nil {
				fmt.Println("Error unmarshaling comp_state:", err)
				return
			}
			fmt.Println("Received comp_state:", comp_state)

		case "DB.Info":
			err = json.Unmarshal(msg.Data, &DB.Info)
			if err != nil {
				fmt.Println("Error unmarshaling DB.Info:", err)
				return
			}
			fmt.Println("Received DB.Info")

		case "offline_download":
			err = json.Unmarshal(msg.Data, &offline_download)
			if err != nil {
				fmt.Println("Error unmarshaling offline_download:", err)
				return
			}
			fmt.Println("Received offline_download")

		default:
			fmt.Println("Unknown message type:", msg.Type)
		}
	}

	client_shared_state := pi.DecompressState(DB.Info, p, comp_state)

	fmt.Println("Building query...")
	num_queries := uint64(len(i))
	if DB.Data.Rows/num_queries < DB.Info.Ne {
		panic("Too many queries to handle!")
	}
	batch_sz := DB.Data.Rows / (DB.Info.Ne * num_queries) * DB.Data.Cols
	bw := float64(0)
	var client_state []pir.State
	var query pir.MsgSlice
	for index, _ := range i {
		index_to_query := i[index] + uint64(index)*batch_sz
		cs, q := pi.Query(index_to_query, client_shared_state, p, DB.Info)
		client_state = append(client_state, cs)
		query.Data = append(query.Data, q)
	}

	comm := float64(query.Size() * uint64(p.Logq) / (8.0 * 1024.0))
	fmt.Printf("\t\tOnline upload: %f KB\n", comm)
	bw += comm
	runtime.GC()

	//发送query给服务器
	queryJSON, _ := json.Marshal(query)
	message := Message{"query", queryJSON}
	err = encoder.Encode(message)
	if err != nil {
		fmt.Println("Error encoding:", err)
		return
	}
	fmt.Printf("发送query成功")

	//接收服务器发送的answer
	var answer pir.Msg
	var msg Message
	err = decoder.Decode(&msg)
	if err != nil {
		fmt.Println("Error decoding:", err)
		return
	}
	err = json.Unmarshal(msg.Data, &answer)
	if err != nil {
		fmt.Println("Error unmarshaling answer:", err)
		return
	}
	fmt.Println("Received answer")

	fmt.Println("Reconstructing...")
	for index, _ := range i {
		index_to_query := i[index] + uint64(index)*batch_sz
		val := pi.Recover(index_to_query, uint64(index), offline_download,
			query.Data[index], answer, client_shared_state,
			client_state[index], p, DB.Info)

		//发送index_to_query和val给服务器
		indexToQueryJSON, _ := json.Marshal(index_to_query)
		valJSON, _ := json.Marshal(val)
		message2 := []Message{{"index_to_query", indexToQueryJSON},
			{"val", valJSON}}
		for _, msg := range message2 {
			err := encoder.Encode(msg)
			if err != nil {
				fmt.Println("Error encoding:", err)
				return
			}
		}
		fmt.Printf("发送index_to_query和val成功")
	}

	fmt.Println("recover Success!")

}
