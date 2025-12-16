#  Arquivo: k_armor_core/k_armor_cli.py

import argparse
from core_engine import gerar_chave, salvar_chave_em_arquivo, carregar_chave, criptografar_arquivo, descriptografar_arquivo

def main():
    parser = argparse.ArgumentParser(description="K-Armor CLI: proteção de arquivos com chave simétrica.")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    parser_gerar = subparsers.add_parser("gerar-chave")
    parser_gerar.add_argument("saida", help="Caminho do arquivo para salvar a chave")

    parser_cript = subparsers.add_parser("criptografar")
    parser_cript.add_argument("arquivo", help="Arquivo a ser criptografado")
    parser_cript.add_argument("chave", help="Caminho da chave")

    parser_descript = subparsers.add_parser("descriptografar")
    parser_descript.add_argument("arquivo_enc", help="Arquivo criptografado (.enc)")
    parser_descript.add_argument("chave", help="Caminho da chave")

    args = parser.parse_args()

    if args.comando == "gerar-chave":
        chave = gerar_chave()
        salvar_chave_em_arquivo(args.saida, chave)
        print(f"[] Chave gerada e salva em: {args.saida}")

    elif args.comando == "criptografar":
        chave = carregar_chave(args.chave)
        criptografar_arquivo(args.arquivo, chave)
        print(f"[] Arquivo criptografado: {args.arquivo}.enc")

    elif args.comando == "descriptografar":
        chave = carregar_chave(args.chave)
        descriptografar_arquivo(args.arquivo_enc, chave)
        print(f"[] Arquivo restaurado: {args.arquivo_enc.replace('.enc', '')}")

if __name__ == "__main__":
    main()
