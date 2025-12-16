# KayosCrypto Ultimate – Especificação Matemática Interna

**Data**: 17 de Novembro de 2025  
**Versão do Algoritmo**: ULTIMATE v5.0.1  
**Escopo**: Descrever formalmente a transformação criptográfica empregada pelo `KayosCryptoUltimate`, com ênfase nas definições matemáticas, reversibilidade e nos pontos que ainda carecem de demonstração/validação formal.

---

## 1. Notação e Domínio
- \( \mathcal{P} = \{0,1\}^* \): conjunto de strings de bits de comprimento arbitrário (plaintexts).
- \( \mathcal{C} = \{0,1\}^* \): conjunto de ciphertexts com mesmo comprimento do plaintext (após padding par).
- \( \mathcal{K} = \{0,1\}^* \): conjunto de senhas finitas (strings UTF-8).
- \( |x| \): comprimento em bytes de \( x \).
- Operações sobre bytes usam aritmética módulo \(256\). Vetores são indexados a partir de 0.
- Permutações são representadas por \(\pi: \{0,\ldots,n-1\} \rightarrow \{0,\ldots,n-1\}\) bijetiva.

O algoritmo processa blocos arbitrários, mantendo reversibilidade exata. Para comprimentos ímpares, um byte zero é anexado temporariamente antes da fase Feistel.

---

## 2. Derivação de Chave
Dada uma senha \( s \in \mathcal{K} \) e tamanho \( m = |P| \), a chave base \( K \in \{0,1\}^{32} \) é obtida por PBKDF2 com SHA3-256:
\[
K = \text{PBKDF2}_{\text{SHA3-256}}(s, \, \text{salt}, \, 100\,000, \, 32)\quad \text{com}\quad \text{salt} = \text{"kayos\_ultimate\_v1_"} \parallel m_{64},
\]
onde \( m_{64} \) é a codificação de \( m \) em 64 bits big-endian.

Os ângulos geométricos derivam dos 64 bits mais significativos de \( K \):
\[
\theta_1 = 2\pi \cdot ((\text{int}(K_0^{63}) \bmod 360) / 360),\quad
\theta_2 = 2\pi \cdot (((\text{int}(K_0^{63}) / 360) \bmod 360) / 360).
\]
Definimos \( \Theta = (\theta_1, \theta_2) \).

---

## 3. Fase Geométrica (Permutações + Misturas)
Esta fase aplica \(L\) camadas (\(1 \leq L \leq 5\)) de transformações. Cada camada \(i\) executa, em ordem:

### 3.1 Permutação Espiral Fibonacci
Constrói-se \( \pi^{(F)}_i \) a partir de rotações circulares pelos primeiros termos da sequência Fibonacci (até 144) alternando sinais, aplicadas sobre o vetor de índices. Se a sequência gerar colisões, usa-se um RNG determinístico \(\text{MT}(\text{SHA256}(\Theta \parallel \text{"fibonacci"}))\) para embaralhar. A transformação é
\[ X \mapsto X \circ \pi^{(F)}_i. \]

### 3.2 Substituição S-Box
Existe uma S-box global \( S: \{0,\ldots,255\} \rightarrow \{0,\ldots,255\} \) construída embaralhando a identidade com sementes derivadas de \( \pi, e, \varphi, \sqrt{2} \). Para cada camada, aplica-se
\[ x_j \mapsto (S(x_j) + i) \bmod 256. \]
A inversa usa \( S^{-1} \) e subtrai o deslocamento \( i \bmod 256 \).

### 3.3 Permutação Ezekiel (Rodas Concêntricas)
Define-se para cada posição \(j\):
\[
\rho_j = \sum_{t=1}^{k} \sin\big(\theta_t + 0{,}1 \cdot t \cdot j\big),
\]
com \(k = 2\) rodas na implementação atual. Ordenando \( \rho_j \) ascendentemente obtém-se uma permutação \( \pi^{(E)}_i \); aplica-se \( X \mapsto X \circ \pi^{(E)}_i. \)

### 3.4 Permutação Razão Áurea
Para cada posição \(j\) define-se
\[
\gamma_j = (j \cdot \varphi \cdot (1 + \theta_2)) \bmod n,
\]
com \( \varphi = 1{,}618... \). Ordenando \( \gamma_j \) gera-se \( \pi^{(G)} \); aplica-se \( X \mapsto X \circ \pi^{(G)}. \)

### 3.5 Mistura Intercamada (se \(i < L-1\))
Usa-se o motor \(\text{StrongMix}\) com chave \( K \parallel \text{"layer"} \parallel i \). Para cada byte \(x_j\) e rodada \(r\) (total de 4):
1. \( x_j \leftarrow x_j \oplus k_{(j + 7r) \bmod |K|} \).
2. \( x_j \leftarrow x_j \oplus (x_{j-3} \gg 2) \) se \( j \ge 3 \).
3. \( x_j \leftarrow x_j \oplus ((x_{j+3} \ll 2) \bmod 256) \) se \( j \le n-4 \).
4. \( x_j \leftarrow (x_j + x_{j-d}) \bmod 256 \) com \( d = (j \bmod 5)+1 \) quando \(j \ge d\).
5. Ao fim de cada rodada, pares \( (x_{2t}, x_{2t+1}) \) são trocados.

Todas as operações são invertíveis byte-a-byte; para descriptografia o código reexecuta o mesmo operador na ordem inversa das fases.

---

## 4. Fase Feistel Geométrica
### 4.1 Preparação
Se \(n = |X|\) pós Fase 1 for ímpar, concatena-se 0 (padding simétrico). Divide-se em metades \(L_0, R_0 \in \{0,1\}^{n/2}\).

### 4.2 Chaves de Rodada
Para cada rodada \( r \in \{0,\ldots,R-1\} \) com \(R=8\):
\[
K_r = \text{SHA3-256}\big(K \parallel r_{32} \parallel n_{64}\big).
\]

### 4.3 Função de Rodada
Dado \(R_r\) e \(K_r\):
1. **Rotação Fibonacci**: para cada byte índice \(j\), define-se \( s = (j \cdot f_r) \bmod 8 \), com \( f_r \) o termo Fibonacci \(r\)-ésimo (sequência cíclica). Calcula-se \( y_j = \text{ROL}_8(R_{r,j}, s) \).
2. **XOR com chave**: \( y_j \leftarrow y_j \oplus (K_r)_j. \)
3. **Mistura Razão Áurea**: \( y_j \leftarrow (y_j + y_{\lfloor (j \varphi) \bmod |y| \rfloor}) \bmod 256. \)
4. **Transformação Ezekiel**: \( y_j \leftarrow (y_j + \lfloor 127 \cdot \sin(\alpha_r + 0{,}1j) \rfloor ) \bmod 256\), com \( \alpha_r = r\pi/4 \).

A saída da função é \( F(R_r, K_r) = y \).

### 4.4 Iteração Feistel
Para cada rodada:
\[
L_{r+1} = R_r,\quad R_{r+1} = L_r \oplus F(R_r, K_r).
\]
O texto cifrado após R rodadas é \( C = L_R \parallel R_R \). A estrutura Feistel garante reversibilidade: descriptografia executa as rodadas com chaves em ordem inversa.

---

## 5. Fase de Pós-Processamento
Aplica-se \(\text{StrongMix}\) novamente com chave \( K \parallel \text{"final"} \). Esta operação é autoinversa porque a implementação usa o mesmo circuito na descriptografia (propriedade explorada em `strong_avalanche_mix`).

---

## 6. Gancho Quântico (Opcional)
Se `use_quantum_assurance = True`, o fluxo agrega snapshots (comprimento, fase) e aciona hooks em `src/quantum`. Esta etapa NÃO modifica a definição matemática principal quando hooks mantêm o ciphertext (comportamento padrão).

---

## 7. Reversibilidade
- Cada permutação \( \pi \) aplicada tem inversa explícita utilizada na descriptografia.
- A S-box e seu inverso satisfazem \( S^{-1}(S(x)) = x \).
- O operador `StrongMix` usa apenas XOR, adição módulo 256 e trocas simétricas, sendo involutivo quando reexecutado com os mesmos parâmetros.
- A rede Feistel é classicamente reversível: o mapeamento \( (L_r, R_r) \mapsto (L_{r+1}, R_{r+1}) \) é bijetivo.

Logo, para toda senha \( s \) e dados \( P \), temos
\[
\text{Decrypt}(\text{Encrypt}(P, s), s) = P.
\]

---

## 8. Considerações de Segurança Matemática
1. **Difusão/Avalanche**: medições internas indicam ~48,47% de bits alterados quando 1 bit do plaintext varia. A fase Feistel e os mixes lineares não possuem demonstração formal de avalanche mínima; os valores são empíricos.
2. **Independência de chave**: PBKDF2 com 100k iterações e SHA3-256 fornece resistência padrão a força bruta, mas não há prova de KDF adequado sob modelos avançados.
3. **Uso de floats**: funções trigonométricas (sin) e números reais (\(\varphi\)) são aproximados em dupla precisão e projetados módulo 256. Não há prova de comportamento uniforme desses offsets.
4. **Pseudo-aleatoriedade**: fallback da permutação Fibonacci depende de Mersenne Twister determinístico; não há prova de que a distribuição resultante seja indistinguível.
5. **Constância Temporal**: o código Python/NumPy possui laços e acessos dependentes dos dados; não é constant-time. Operações com `numpy.sin` e permutações baseadas em ordenações introduzem variação temporal detectável.

---

## 9. Lacunas para Declarar Alta Segurança Criptoanalítica
- **Prova formal**: não existe demonstração de que a composição das fases resista a ataques diferenciais/lineares ou que o espaço de permutações atinja uma classe segura.
- **Criptoanálise adversarial**: faltam campanhas sistemáticas (diferential trail search, boomerang, meet-in-the-middle) documentadas.
- **Side-channel**: ausência de revisão constant-time e de medições de tempo/janela eletromagnética.

Enquanto essas lacunas persistirem, a classificação “alto risco” depende de métricas operacionais internas (vide `reports/quantum/high_risk_readiness.json`), mas não se traduz em garantia matemática robusta.

---

## 10. Sumário dos Testes Existentes
- `make test` (9/9) cobre reversibilidade, avalanche empírico, performance mínima.
- `tools/generate_high_risk_readiness.py` produz relatórios com score \(0{,}9804\), throughput 14,64 MB/s.
- Ainda não há suíte formal de criptoanálise automatizada registrada no repositório.

---

## 11. Próximos Passos Recomendados
1. **Formalização**: traduzir cada fase para um modelo algébrico (ex.: permutações descritas como matrizes de permutação) e estudar a composição em \( S_n \).
2. **Prova de segurança**: buscar argumentos de indistinguibilidade sob ataque escolhido (CPA) ou resistência diferencial via bounds nas probabilidades diferenciais das S-boxes e da função de rodada.
3. **Criptoanálise experimental**: construir suíte de ataques diferenciais/lineares para \(R=8\) e para versões reduzidas, registrando probabilidades empíricas.
4. **Constant-time**: reimplementar as fases críticas (S-box, Feistel) em linguagem de baixo nível com disciplina de acesso independente da chave/dados.

---

### Conclusão
O algoritmo KayosCrypto Ultimate é matematicamente bem definido e reversível por construção. Porém, na ausência das provas e baterias descritas na Seção 9, não se pode declarar prontidão total para ambientes de alto risco sob critérios criptográficos formais, apesar do score operacional interno elevado.
