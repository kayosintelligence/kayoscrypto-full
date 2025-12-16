# Go Example

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
    "os"
)

type EntropyRequest struct {
    Bytes int `json:"bytes"`
}

type EntropyResponse struct {
    Data  string `json:"data"`
    Sator struct {
        Score float64 `json:"score"`
    } `json:"sator"`
}

func main() {
    token := os.Getenv("KAYOSCRYPTO_TOKEN")
    body, _ := json.Marshal(EntropyRequest{Bytes: 4096})

    req, _ := http.NewRequest(
        http.MethodPost,
        "https://api.kayoscrypto.dev/v1/entropy/stream",
        bytes.NewReader(body),
    )
    req.Header.Set("Authorization", "Bearer "+token)
    req.Header.Set("Content-Type", "application/json")

    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        panic(err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        panic(fmt.Sprintf("unexpected status: %d", resp.StatusCode))
    }

    var payload EntropyResponse
    if err := json.NewDecoder(resp.Body).Decode(&payload); err != nil {
        panic(err)
    }

    fmt.Println("entropy", payload.Data)
    fmt.Println("sator_score", payload.Sator.Score)
}
```
