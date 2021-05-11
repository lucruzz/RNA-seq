# Script pega a saída partida do HTSeq com 25 partes e une em 2 colunas
# Basicamente, ele vai somar as leituras já mapeadas pelo HTSeq
# Para executar: python3 HTSeq_count.py <<filename_input>>.count <<filename_output>>.merge.count <<n_splited_files>>
import sys

file_name_in = sys.argv[1]
file_name_out = sys.argv[2]
n_colummns = int(sys.argv[3])

HTSeq_file = open(file_name_in, "r")
HTSeq_new_file = open(file_name_out, "w")

n_colummns += 1

for linha in HTSeq_file:
    soma = 0
    valores = linha.split()
    for i in range(1,n_colummns):
        soma = int(valores[i]) + soma 
    a = valores[0] + '\t' + str(soma) + '\n'
    HTSeq_new_file.write(a)

HTSeq_file.close()
HTSeq_new_file.close()
