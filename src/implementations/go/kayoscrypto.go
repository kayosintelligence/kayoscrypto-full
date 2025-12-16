// Package kayoscrypto provides geometric cryptographic operations
// based on Fibonacci sequences, golden ratio rotations, and multi-layer transformations.
//
// This is the Go implementation of KayosCrypto v5.0.1 ULTIMATE.
//
// Architecture: Fishbone (Spine + 3 Ribs)
// - Rib 1: Fibonacci Direction
// - Rib 2: Multi-layer Rotation (Ezekiel Concentric)
// - Rib 3: Core System (Geometric Permutation + Feistel)
//
// Patents: BR 10 2025 026228-2 | BR 10 2025 026547-8
// Trademark: BR 51 2025 003443-1 (KAYOS)
//
// Author: KAYOS Quantum Research Lab
// Date: December 2, 2025

package kayoscrypto

import (
	"crypto/sha256"
	"errors"
	"math"
)

// PHI is the golden ratio
const PHI = 1.618033988749895

// PHI_INV is the inverse of the golden ratio
const PHI_INV = 0.618033988749895

// FibonacciSequence generates Fibonacci numbers up to n terms
func FibonacciSequence(n int) []int {
	if n <= 0 {
		return []int{}
	}
	if n == 1 {
		return []int{1}
	}
	
	fib := make([]int, n)
	fib[0] = 1
	fib[1] = 1
	
	for i := 2; i < n; i++ {
		fib[i] = fib[i-1] + fib[i-2]
	}
	
	return fib
}

// DeriveKey derives a key from password using SHA-256
func DeriveKey(password string, length int) []byte {
	hash := sha256.Sum256([]byte(password))
	key := hash[:]
	
	// Extend if needed
	for len(key) < length {
		newHash := sha256.Sum256(key)
		key = append(key, newHash[:]...)
	}
	
	return key[:length]
}

// CircularShift performs a circular shift on a byte slice
func CircularShift(data []byte, shift int) []byte {
	n := len(data)
	if n == 0 {
		return data
	}
	
	// Normalize shift
	shift = ((shift % n) + n) % n
	
	result := make([]byte, n)
	for i := 0; i < n; i++ {
		newIndex := (i + shift) % n
		result[newIndex] = data[i]
	}
	
	return result
}

// CircularShiftReverse reverses a circular shift
func CircularShiftReverse(data []byte, shift int) []byte {
	return CircularShift(data, -shift)
}

// =====================================
// RIB 1: Fibonacci Direction
// =====================================

// FibonacciDirection implements the Fibonacci-based direction transformation
type FibonacciDirection struct {
	fibSequence []int
	mode        int
}

// NewFibonacciDirection creates a new FibonacciDirection instance
func NewFibonacciDirection(sequenceLength int) *FibonacciDirection {
	return &FibonacciDirection{
		fibSequence: FibonacciSequence(sequenceLength),
		mode:        0,
	}
}

// DetermineMode derives transformation mode from key
func (fd *FibonacciDirection) DetermineMode(key []byte) int {
	if len(key) == 0 {
		return 0
	}
	
	// Sum key bytes and mod by sequence length
	sum := 0
	for _, b := range key {
		sum += int(b)
	}
	
	fd.mode = sum % len(fd.fibSequence)
	return fd.mode
}

// Apply applies Fibonacci direction transformation
func (fd *FibonacciDirection) Apply(data []byte, key []byte) []byte {
	if len(data) == 0 {
		return data
	}
	
	fd.DetermineMode(key)
	result := make([]byte, len(data))
	copy(result, data)
	
	// Apply Fibonacci-based shifts
	for i, fibVal := range fd.fibSequence {
		if i >= len(result) {
			break
		}
		
		direction := 1
		if fd.mode%2 == 0 {
			direction = -1
		}
		
		shift := fibVal * direction
		result = CircularShift(result, shift)
	}
	
	return result
}

// Reverse reverses Fibonacci direction transformation
func (fd *FibonacciDirection) Reverse(data []byte, key []byte) []byte {
	if len(data) == 0 {
		return data
	}
	
	fd.DetermineMode(key)
	result := make([]byte, len(data))
	copy(result, data)
	
	// Reverse Fibonacci shifts (opposite order and direction)
	for i := len(fd.fibSequence) - 1; i >= 0; i-- {
		fibVal := fd.fibSequence[i]
		if i >= len(result) {
			continue
		}
		
		direction := 1
		if fd.mode%2 == 0 {
			direction = -1
		}
		
		shift := fibVal * direction
		result = CircularShiftReverse(result, shift)
	}
	
	return result
}

// =====================================
// RIB 2: Ezekiel Concentric Engine
// =====================================

// EzekielWheel represents a single rotation wheel
type EzekielWheel struct {
	name     string
	ratio    float64
	position float64
}

// EzekielConcentric implements the multi-layer rotation system
type EzekielConcentric struct {
	mainWheel  *EzekielWheel
	alphaWheel *EzekielWheel
	betaWheel  *EzekielWheel
}

// NewEzekielConcentric creates a new EzekielConcentric engine
func NewEzekielConcentric() *EzekielConcentric {
	return &EzekielConcentric{
		mainWheel:  &EzekielWheel{name: "Main", ratio: PHI, position: 0},
		alphaWheel: &EzekielWheel{name: "Alpha", ratio: PHI_INV, position: 0},
		betaWheel:  &EzekielWheel{name: "Beta", ratio: math.Pi / PHI, position: 0},
	}
}

// ComputeRotation computes rotation amount for a wheel (stateless - pure function)
func (w *EzekielWheel) ComputeRotation(input float64) float64 {
	rotation := input * w.ratio
	return math.Mod(rotation, 2*math.Pi)
}

// computeShifts computes all three rotation shifts from key (deterministic)
func (ec *EzekielConcentric) computeShifts(key []byte, dataLen int) (int, int, int) {
	// Derive rotation seed from key
	keySum := 0.0
	for _, b := range key {
		keySum += float64(b)
	}
	keySum = keySum / 256.0 // Normalize
	
	// Compute three perpendicular rotations
	mainRot := ec.mainWheel.ComputeRotation(keySum)
	alphaRot := ec.alphaWheel.ComputeRotation(keySum * PHI)
	betaRot := ec.betaWheel.ComputeRotation(keySum * PHI_INV)
	
	// Convert rotations to byte shifts
	mainShift := int(mainRot * float64(dataLen) / (2 * math.Pi))
	alphaShift := int(alphaRot * float64(dataLen) / (2 * math.Pi))
	betaShift := int(betaRot * float64(dataLen) / (2 * math.Pi))
	
	return mainShift, alphaShift, betaShift
}

// Apply applies multi-layer rotation transformation
func (ec *EzekielConcentric) Apply(data []byte, key []byte) []byte {
	if len(data) == 0 {
		return data
	}
	
	result := make([]byte, len(data))
	copy(result, data)
	
	mainShift, alphaShift, betaShift := ec.computeShifts(key, len(data))
	
	// Apply shifts in order: main → alpha → beta
	result = CircularShift(result, mainShift)
	result = CircularShift(result, alphaShift)
	result = CircularShift(result, betaShift)
	
	return result
}

// Reverse reverses multi-layer rotation transformation
func (ec *EzekielConcentric) Reverse(data []byte, key []byte) []byte {
	if len(data) == 0 {
		return data
	}
	
	result := make([]byte, len(data))
	copy(result, data)
	
	mainShift, alphaShift, betaShift := ec.computeShifts(key, len(data))
	
	// Reverse shifts in opposite order: beta → alpha → main
	result = CircularShiftReverse(result, betaShift)
	result = CircularShiftReverse(result, alphaShift)
	result = CircularShiftReverse(result, mainShift)
	
	return result
}

// =====================================
// RIB 3: Core System
// =====================================

// GeometricPermutation implements geometric permutation engine
type GeometricPermutation struct {
	blockSize int
}

// NewGeometricPermutation creates a new GeometricPermutation engine
func NewGeometricPermutation(blockSize int) *GeometricPermutation {
	if blockSize <= 0 {
		blockSize = 16
	}
	return &GeometricPermutation{blockSize: blockSize}
}

// GeneratePermutation generates a permutation based on key
func (gp *GeometricPermutation) GeneratePermutation(key []byte, size int) []int {
	perm := make([]int, size)
	for i := 0; i < size; i++ {
		perm[i] = i
	}
	
	// Fisher-Yates shuffle seeded by key
	keyIndex := 0
	for i := size - 1; i > 0; i-- {
		// Use key bytes to determine swap
		j := int(key[keyIndex%len(key)]) % (i + 1)
		perm[i], perm[j] = perm[j], perm[i]
		keyIndex++
	}
	
	return perm
}

// InversePermutation computes the inverse of a permutation
func (gp *GeometricPermutation) InversePermutation(perm []int) []int {
	inverse := make([]int, len(perm))
	for i, v := range perm {
		inverse[v] = i
	}
	return inverse
}

// Apply applies geometric permutation
func (gp *GeometricPermutation) Apply(data []byte, key []byte) []byte {
	if len(data) == 0 {
		return data
	}
	
	perm := gp.GeneratePermutation(key, len(data))
	result := make([]byte, len(data))
	
	for i, p := range perm {
		result[p] = data[i]
	}
	
	return result
}

// Reverse reverses geometric permutation
func (gp *GeometricPermutation) Reverse(data []byte, key []byte) []byte {
	if len(data) == 0 {
		return data
	}
	
	perm := gp.GeneratePermutation(key, len(data))
	inverse := gp.InversePermutation(perm)
	result := make([]byte, len(data))
	
	for i, p := range inverse {
		result[p] = data[i]
	}
	
	return result
}

// FeistelNetwork implements a Feistel cipher network
type FeistelNetwork struct {
	rounds int
}

// NewFeistelNetwork creates a new FeistelNetwork
func NewFeistelNetwork(rounds int) *FeistelNetwork {
	if rounds <= 0 {
		rounds = 4
	}
	return &FeistelNetwork{rounds: rounds}
}

// roundFunction is the Feistel round function
func (fn *FeistelNetwork) roundFunction(data []byte, roundKey []byte) []byte {
	result := make([]byte, len(data))
	for i := range data {
		result[i] = data[i] ^ roundKey[i%len(roundKey)]
	}
	return result
}

// Apply applies Feistel network encryption
func (fn *FeistelNetwork) Apply(data []byte, key []byte) []byte {
	if len(data) < 2 {
		return data
	}
	
	mid := len(data) / 2
	left := make([]byte, mid)
	right := make([]byte, len(data)-mid)
	copy(left, data[:mid])
	copy(right, data[mid:])
	
	for round := 0; round < fn.rounds; round++ {
		// Derive round key
		roundKey := DeriveKey(string(key)+string(rune(round)), len(right))
		
		// Feistel operation
		newLeft := right
		f := fn.roundFunction(right, roundKey)
		newRight := make([]byte, len(left))
		for i := range left {
			newRight[i] = left[i] ^ f[i%len(f)]
		}
		
		left = newLeft
		right = newRight
	}
	
	// Combine
	result := make([]byte, len(data))
	copy(result[:mid], left)
	copy(result[mid:], right)
	
	return result
}

// Reverse reverses Feistel network encryption
func (fn *FeistelNetwork) Reverse(data []byte, key []byte) []byte {
	if len(data) < 2 {
		return data
	}
	
	mid := len(data) / 2
	left := make([]byte, mid)
	right := make([]byte, len(data)-mid)
	copy(left, data[:mid])
	copy(right, data[mid:])
	
	// Reverse rounds
	for round := fn.rounds - 1; round >= 0; round-- {
		roundKey := DeriveKey(string(key)+string(rune(round)), len(left))
		
		// Reverse Feistel operation
		newRight := left
		f := fn.roundFunction(left, roundKey)
		newLeft := make([]byte, len(right))
		for i := range right {
			newLeft[i] = right[i] ^ f[i%len(f)]
		}
		
		left = newLeft
		right = newRight
	}
	
	result := make([]byte, len(data))
	copy(result[:mid], left)
	copy(result[mid:], right)
	
	return result
}

// =====================================
// MAIN: KayosCrypto Ultimate
// =====================================

// KayosCrypto is the main encryption engine
type KayosCrypto struct {
	fibDirection    *FibonacciDirection
	ezekielEngine   *EzekielConcentric
	geometricPerm   *GeometricPermutation
	feistelNetwork  *FeistelNetwork
	useConcentric   bool
	useDirection    bool
}

// NewKayosCrypto creates a new KayosCrypto instance
func NewKayosCrypto(useConcentric, useDirection bool) *KayosCrypto {
	return &KayosCrypto{
		fibDirection:    NewFibonacciDirection(20),
		ezekielEngine:   NewEzekielConcentric(),
		geometricPerm:   NewGeometricPermutation(16),
		feistelNetwork:  NewFeistelNetwork(4),
		useConcentric:   useConcentric,
		useDirection:    useDirection,
	}
}

// Encrypt encrypts data with the given password
func (kc *KayosCrypto) Encrypt(plaintext []byte, password string, level int) ([]byte, error) {
	if len(plaintext) == 0 {
		return nil, errors.New("empty plaintext")
	}
	if password == "" {
		return nil, errors.New("empty password")
	}
	if level < 1 || level > 3 {
		level = 3
	}
	
	key := DeriveKey(password, 32)
	result := make([]byte, len(plaintext))
	copy(result, plaintext)
	
	// Phase 1: Fibonacci Direction (if enabled)
	if kc.useDirection && level >= 1 {
		result = kc.fibDirection.Apply(result, key)
	}
	
	// Phase 2: Multi-layer Rotation (if enabled)
	if kc.useConcentric && level >= 2 {
		result = kc.ezekielEngine.Apply(result, key)
	}
	
	// Phase 3: Core System (always applied)
	if level >= 3 {
		result = kc.geometricPerm.Apply(result, key)
		result = kc.feistelNetwork.Apply(result, key)
	}
	
	return result, nil
}

// Decrypt decrypts data with the given password
func (kc *KayosCrypto) Decrypt(ciphertext []byte, password string, level int) ([]byte, error) {
	if len(ciphertext) == 0 {
		return nil, errors.New("empty ciphertext")
	}
	if password == "" {
		return nil, errors.New("empty password")
	}
	if level < 1 || level > 3 {
		level = 3
	}
	
	key := DeriveKey(password, 32)
	result := make([]byte, len(ciphertext))
	copy(result, ciphertext)
	
	// Reverse order: Phase 3 → Phase 2 → Phase 1
	
	// Phase 3: Core System (always applied)
	if level >= 3 {
		result = kc.feistelNetwork.Reverse(result, key)
		result = kc.geometricPerm.Reverse(result, key)
	}
	
	// Phase 2: Multi-layer Rotation (if enabled)
	if kc.useConcentric && level >= 2 {
		result = kc.ezekielEngine.Reverse(result, key)
	}
	
	// Phase 1: Fibonacci Direction (if enabled)
	if kc.useDirection && level >= 1 {
		result = kc.fibDirection.Reverse(result, key)
	}
	
	return result, nil
}

// Version returns the version string
func Version() string {
	return "KayosCrypto Go v5.0.1 ULTIMATE"
}
