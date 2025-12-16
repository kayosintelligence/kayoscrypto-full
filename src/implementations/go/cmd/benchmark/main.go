package main

import (
"fmt"
"time"

kayos "kayoscrypto"
)

func main() {
fmt.Println("🚀 KayosCrypto Go Quick Benchmark\n")

password := "KayosCrypto-Benchmark-Key-2025"
cipher := kayos.NewKayosCrypto(true, true)

sizes := []struct {
size int
label string
}{
{1024, "1 KB"},
{10 * 1024, "10 KB"},
{50 * 1024, "50 KB"},
}

fmt.Println("| Size  | Time (ms) | Throughput  | vs Python 308 KB/s |")
fmt.Println("|-------|-----------|-------------|-------------------|")

for _, s := range sizes {
plaintext := make([]byte, s.size)
for i := range plaintext {
plaintext[i] = byte(i % 256)
}

// Warmup
cipher.Encrypt(plaintext, password, 3)

// Benchmark (10 iterations)
start := time.Now()
for i := 0; i < 10; i++ {
cipher.Encrypt(plaintext, password, 3)
}
elapsed := time.Since(start)
timePerOp := float64(elapsed.Milliseconds()) / 10.0
throughputKBs := float64(s.size) / (elapsed.Seconds() / 10.0) / 1024.0
speedup := throughputKBs / 308.0

fmt.Printf("| %5s | %9.2f | %8.0f KB/s | %5.1fx faster     |\n",
s.label, timePerOp, throughputKBs, speedup)
}

// Verify
fmt.Println("\n✅ Verification:")
test := []byte("KayosCrypto Go Test")
enc, _ := cipher.Encrypt(test, password, 3)
dec, _ := cipher.Decrypt(enc, password, 3)

match := len(dec) == len(test)
if match {
for i := range test {
if dec[i] != test[i] {
match = false
break
}
}
}

if match {
fmt.Println("   Encrypt/Decrypt: PASSED")
} else {
fmt.Println("   Encrypt/Decrypt: FAILED")
}
}
