package main

import (
	"GoProject/pir"
	"encoding/json"
	"fmt"
	"net"
	"runtime"
	"time"
)

const LOGQ = uint64(32)
const SEC_PARAM = uint64(1 << 10)

type Message struct {
	Type string
	Data []byte
}

func process(conn net.Conn) {
	//关闭连接
	defer conn.Close()

	encoder := json.NewEncoder(conn)
	decoder := json.NewDecoder(conn)

	// PIR scheme initialization
	N := uint64(1 << 28)
	d := uint64(3)
	pi := pir.DoublePIR{}
	p := pi.PickParams(N, d, SEC_PARAM, LOGQ)
	DB := pir.MakeRandomDB(N, d, &p)
	fmt.Printf("Executing %s\n", pi.Name())

	server_shared_state, comp_state := pi.InitCompressed(DB.Info, p)
	bw := float64(0)

	fmt.Println("Setup...")
	start := time.Now()
	server_state, _ := pi.Setup(DB, server_shared_state, p)
	pir.PrintTime(start)
	comm := float64(0)
	fmt.Printf("\t\tOffline download: %f KB\n", comm)
	bw += comm
	runtime.GC()

	// 发送comp_state和DB.Info和offline_download给客户端
	compStateJSON, _ := json.Marshal(comp_state)
	dbInfoJSON, _ := json.Marshal(DB.Info)
	//offline_downloadJSON, _ := json.Marshal(offline_download)
	message := []Message{
		{"comp_state", compStateJSON},
		{"DB.Info", dbInfoJSON},
		//{"offline_download", offline_downloadJSON},
	}
	for _, msg := range message {
		err := encoder.Encode(msg)
		if err != nil {
			fmt.Println("Error encoding:", err)
			return
		}
	}
	fmt.Printf("发送comp_state和DB.Info和offline_download成功")

	// 接收client发送的query
	var query pir.MsgSlice
	var msg Message
	err := decoder.Decode(&msg)
	if err != nil {
		fmt.Println("Error decoding:", err)
		return
	}
	err = json.Unmarshal(msg.Data, &query)
	if err != nil {
		fmt.Println("Error unmarshaling query:", err)
		return
	}

	fmt.Println("Answering query...")
	start = time.Now()
	answer, offline_download := pi.Answer(DB, query, server_state, server_shared_state, p)
	elapsed := pir.PrintTime(start)
	pir.PrintRate(p, elapsed, 1)
	comm = float64(answer.Size() * uint64(p.Logq) / (8.0 * 1024.0))
	fmt.Printf("\t\tOnline download: %f KB\n", comm)
	bw += comm
	runtime.GC()
	pi.Reset(DB, p)
	fmt.Println("\t\tbw: ", bw)

	//fmt.Println("Answering query for test...")
	//start = time.Now()
	//pi.Answer2(DB, query, server_state, server_shared_state, p)
	//elapsed = pir.PrintTime(start)
	//pir.PrintRate(p, elapsed, 1)
	//runtime.GC()

	// 发送answer给客户端
	answerJSON, _ := json.Marshal(answer)
	offline_downloadJSON, _ := json.Marshal(offline_download)
	message = []Message{{"answer", answerJSON},
		{"offline_download", offline_downloadJSON}}
	for _, msg := range message {
		err := encoder.Encode(msg)
		if err != nil {
			fmt.Println("Error encoding:", err)
			return
		}
	}
	fmt.Printf("发送answer成功")

	// 接收client发送的index_to_query和val
	var index_to_query uint64
	var val uint64
	for i := 0; i < 2; i++ {
		err = decoder.Decode(&msg)
		if err != nil {
			fmt.Println("Error decoding:", err)
			return
		}
		if i == 0 {
			err = json.Unmarshal(msg.Data, &index_to_query)
			if err != nil {
				fmt.Println("Error unmarshaling index_to_query:", err)
				return
			}
		} else {
			err = json.Unmarshal(msg.Data, &val)
			if err != nil {
				fmt.Println("Error unmarshaling val:", err)
				return
			}
		}
	}

	//检测是否恢复成功
	index := index_to_query
	if DB.GetElem(index_to_query) != val {
		fmt.Printf("Batch %d (querying index %d -- row should be >= %d): Got %d instead of %d\n",
			index, index_to_query, DB.Data.Rows/4, val, DB.GetElem(index_to_query))
		panic("Reconstruct failed!")
	}
	fmt.Println("recover success!")

}

func main() {

	fmt.Println("服务器启动...")

	// 监听
	listen, err := net.Listen("tcp", "0.0.0.0:8000")
	if err != nil {
		fmt.Println("监听失败，err:", err)
		return
	}

	//循环等待客户端连接
	for {
		conn, err2 := listen.Accept()
		if err2 != nil {
			fmt.Println("接受失败，err:", err2)
		} else {
			fmt.Printf("接受成功...,conn=%v, 客户端信息%v\n", conn, conn.RemoteAddr().String())
		}

		// 启动一个协程处理客户端请求
		go process(conn)
	}
}
