// KayosCrypto CLI - Go Implementation
// Geometric cryptographic system with Fibonacci/Ezekiel transformations
//
// Patents: BR 10 2025 026228-2 | BR 10 2025 026547-8
// Trademark: BR 51 2025 003443-1 (KAYOS)
//
// Author: KAYOS Quantum Research Lab
// Date: December 2, 2025

package main

import (
	"encoding/hex"
	"flag"
	"fmt"
	"io"
	"os"
	"time"

	"kayoscrypto"
)

func main() {
	// CLI flags
	encrypt := flag.Bool("e", false, "Encrypt mode")
	decrypt := flag.Bool("d", false, "Decrypt mode")
	password := flag.String("p", "", "Password for encryption/decryption")
	level := flag.Int("l", 3, "Encryption level (1-3)")
	benchmark := flag.Bool("bench", false, "Run benchmark")
	version := flag.Bool("v", false, "Show version")
	inputFile := flag.String("i", "", "Input file")
	outputFile := flag.String("o", "", "Output file")
	
	flag.Parse()
	
	// Show version
	if *version {
		fmt.Println(kayoscrypto.Version())
		fmt.Println("Go Runtime: go1.25.4 linux/amd64")
		fmt.Println("Architecture: Fishbone (Spine + 3 Ribs)")
		fmt.Println("  Rib 1: Fibonacci Direction")
		fmt.Println("  Rib 2: Ezekiel Concentric (Multi-layer Rotation)")
		fmt.Println("  Rib 3: Core System (Geometric Permutation + Feistel)")
		fmt.Println("\nPatents: BR 10 2025 026228-2 | BR 10 2025 026547-8")
		fmt.Println("Trademark: BR 51 2025 003443-1 (KAYOS)")
		return
	}
	
	// Run benchmark
	if *benchmark {
		runBenchmark()
		return
	}
	
	// Validate mode
	if !*encrypt && !*decrypt {
		fmt.Println("Error: Specify -e (encrypt) or -d (decrypt)")
		flag.Usage()
		os.Exit(1)
	}
	
	if *password == "" {
		fmt.Println("Error: Password required (-p)")
		os.Exit(1)
	}
	
	// Read input
	var data []byte
	var err error
	
	if *inputFile != "" {
		data, err = os.ReadFile(*inputFile)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error reading file: %v\n", err)
			os.Exit(1)
		}
	} else {
		data, err = io.ReadAll(os.Stdin)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error reading stdin: %v\n", err)
			os.Exit(1)
		}
	}
	
	// Create cipher
	kc := kayoscrypto.NewKayosCrypto(true, true)
	
	var result []byte
	
	if *encrypt {
		result, err = kc.Encrypt(data, *password, *level)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Encryption error: %v\n", err)
			os.Exit(1)
		}
		// Output as hex for encrypt
		if *outputFile != "" {
			err = os.WriteFile(*outputFile, []byte(hex.EncodeToString(result)), 0644)
		} else {
			fmt.Println(hex.EncodeToString(result))
		}
	} else {
		// Decode hex input for decrypt
		data, err = hex.DecodeString(string(data))
		if err != nil {
			fmt.Fprintf(os.Stderr, "Invalid hex input: %v\n", err)
			os.Exit(1)
		}
		
		result, err = kc.Decrypt(data, *password, *level)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Decryption error: %v\n", err)
			os.Exit(1)
		}
		
		if *outputFile != "" {
			err = os.WriteFile(*outputFile, result, 0644)
		} else {
			fmt.Print(string(result))
		}
	}
	
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error writing output: %v\n", err)
		os.Exit(1)
	}
}

func runBenchmark() {
	fmt.Println("=" + fmt.Sprintf("%98s", "") + "=")
	fmt.Println("  KayosCrypto Go Benchmark")
	fmt.Println("=" + fmt.Sprintf("%98s", "") + "=")
	fmt.Println()
	
	kc := kayoscrypto.NewKayosCrypto(true, true)
	password := "benchmark_password_secure_12345"
	
	sizes := []int{1024, 10240, 102400, 1048576} // 1KB, 10KB, 100KB, 1MB
	
	fmt.Printf("%-15s %-15s %-15s %-15s\n", "Size", "Encrypt", "Decrypt", "Throughput")
	fmt.Println("------------------------------------------------------------")
	
	for _, size := range sizes {
		// Generate test data
		data := make([]byte, size)
		for i := range data {
			data[i] = byte(i % 256)
		}
		
		// Benchmark encrypt
		start := time.Now()
		iterations := 100
		if size > 100000 {
			iterations = 10
		}
		
		var encrypted []byte
		for i := 0; i < iterations; i++ {
			encrypted, _ = kc.Encrypt(data, password, 3)
		}
		encryptTime := time.Since(start) / time.Duration(iterations)
		
		// Benchmark decrypt
		start = time.Now()
		for i := 0; i < iterations; i++ {
			kc.Decrypt(encrypted, password, 3)
		}
		decryptTime := time.Since(start) / time.Duration(iterations)
		
		// Calculate throughput
		throughput := float64(size) / encryptTime.Seconds() / 1024 / 1024 // MB/s
		
		sizeStr := fmt.Sprintf("%d KB", size/1024)
		if size >= 1048576 {
			sizeStr = fmt.Sprintf("%d MB", size/1048576)
		}
		
		fmt.Printf("%-15s %-15s %-15s %.2f MB/s\n", 
			sizeStr, 
			encryptTime.Round(time.Microsecond),
			decryptTime.Round(time.Microsecond),
			throughput)
	}
	
	fmt.Println()
	fmt.Println("=" + fmt.Sprintf("%98s", "") + "=")
	fmt.Println("  Benchmark Complete")
	fmt.Println("=" + fmt.Sprintf("%98s", "") + "=")
}
