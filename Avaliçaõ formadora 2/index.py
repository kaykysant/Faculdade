#!/usr/bin/env python3
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import random

def gerar_temperatura(hora, base_temp=22):
    if 0 <= hora < 6:
        temp = base_temp - 2 + np.random.normal(0, 0.5)
    elif 6 <= hora < 9:
        temp = base_temp - 1 + np.random.normal(0, 0.5)
    elif 9 <= hora < 12:
        temp = base_temp + np.random.normal(0, 0.5)
    elif 12 <= hora < 15:
        temp = base_temp + 2 + np.random.normal(0, 0.5)
    elif 15 <= hora < 18:
        temp = base_temp + 1 + np.random.normal(0, 0.5)
    elif 18 <= hora < 21:
        temp = base_temp + np.random.normal(0, 0.5)
    else:
        temp = base_temp - 1 + np.random.normal(0, 0.5)
    return round(float(temp), 2)

def gerar_luminosidade(hora, dia_semana):
    # dia_semana: 0=Monday ... 6=Sunday
    if dia_semana in [5, 6]:  # fim de semana
        if 8 <= hora < 18:
            lux = np.random.uniform(50, 200)
        else:
            lux = 0
    else:
        if 0 <= hora < 6:
            lux = 0
        elif 6 <= hora < 8:
            lux = np.random.uniform(100, 200)
        elif 8 <= hora < 18:
            lux = np.random.uniform(300, 500)
        elif 18 <= hora < 20:
            lux = np.random.uniform(100, 300)
        elif 20 <= hora < 22:
            lux = np.random.uniform(50, 150)
        else:
            lux = 0
    return round(float(lux), 2)

def gerar_ocupacao(hora, dia_semana):
    if dia_semana in [5, 6]:  # fim de semana
        if 9 <= hora < 17:
            return 1 if random.random() < 0.1 else 0
        else:
            return 0
    else:
        if 7 <= hora < 9:
            return 1 if random.random() < 0.3 else 0
        elif 9 <= hora < 12:
            return 1 if random.random() < 0.9 else 0
        elif 12 <= hora < 13:
            return 1 if random.random() < 0.4 else 0
        elif 13 <= hora < 18:
            return 1 if random.random() < 0.85 else 0
        elif 18 <= hora < 20:
            return 1 if random.random() < 0.3 else 0
        else:
            return 0

def simular_smart_office(data_inicio=None, intervalo_minutos=15, dias=7, seed=None, out_path=None):
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)

    if data_inicio is None:
        data_inicio = datetime(2024, 1, 15, 0, 0, 0)

    total_registros = (dias * 24 * 60) // intervalo_minutos
    dados = []

    sensores_temp = ['TEMP_01', 'TEMP_02', 'TEMP_03']
    sensores_lux = ['LUX_01', 'LUX_02', 'LUX_03']
    sensores_ocup = ['OCUP_01', 'OCUP_02', 'OCUP_03', 'OCUP_04', 'OCUP_05']

    timestamp_atual = data_inicio
    for _ in range(total_registros):
        hora_atual = timestamp_atual.hour
        dia_semana_num = timestamp_atual.weekday()  # 0..6

        for sensor_id in sensores_temp:
            dados.append({
                'timestamp': timestamp_atual,
                'sensor_id': sensor_id,
                'tipo_sensor': 'temperatura',
                'valor': gerar_temperatura(hora_atual),
                'unidade': '°C'
            })

        for sensor_id in sensores_lux:
            dados.append({
                'timestamp': timestamp_atual,
                'sensor_id': sensor_id,
                'tipo_sensor': 'luminosidade',
                'valor': gerar_luminosidade(hora_atual, dia_semana_num),
                'unidade': 'lux'
            })

        for sensor_id in sensores_ocup:
            dados.append({
                'timestamp': timestamp_atual,
                'sensor_id': sensor_id,
                'tipo_sensor': 'ocupacao',
                'valor': gerar_ocupacao(hora_atual, dia_semana_num),
                'unidade': 'boolean'
            })

        timestamp_atual += timedelta(minutes=intervalo_minutos)

    df = pd.DataFrame(dados)
    # garantir coluna de dia da semana consistente (em inglês)
    weekday_map = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
                   4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
    df['weekday_num'] = df['timestamp'].dt.weekday
    df['dia_semana'] = df['weekday_num'].map(weekday_map)
    df['hora'] = df['timestamp'].dt.hour
    df['data'] = df['timestamp'].dt.date

    if out_path:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_path, index=False)
    return df

def gerar_relatorio_resumo(df):
    print("=" * 60)
    print("RELATÓRIO RESUMIDO - SIMULAÇÃO SMART OFFICE")
    print("=" * 60)

    temp_data = df[df['tipo_sensor'] == 'temperatura']
    print(f"\nTEMPERATURA:")
    print(f"  Média geral: {temp_data['valor'].mean():.2f}°C")
    print(f"  Mínima: {temp_data['valor'].min():.2f}°C")
    print(f"  Máxima: {temp_data['valor'].max():.2f}°C")

    lux_data = df[df['tipo_sensor'] == 'luminosidade']
    comercial = lux_data[lux_data['hora'].between(8, 18)]
    print(f"\nLUMINOSIDADE:")
    print(f"  Média durante horário comercial (8h-18h): {comercial['valor'].mean():.2f} lux")
    print(f"  Máxima registrada: {lux_data['valor'].max():.2f} lux")

    ocup_data = df[df['tipo_sensor'] == 'ocupacao']
    print(f"\nOCUPAÇÃO:")
    print(f"  Taxa média de ocupação: {(ocup_data['valor'].mean() * 100):.1f}%")

    print(f"\n  Ocupação por dia da semana:")
    for dia in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        if dia in ocup_data['dia_semana'].unique():
            taxa = ocup_data[ocup_data['dia_semana'] == dia]['valor'].mean() * 100
            print(f"    {dia}: {taxa:.1f}%")

    ocup_horaria = ocup_data.groupby('hora')['valor'].mean()
    hora_pico = int(ocup_horaria.idxmax())
    print(f"\n  Horário de pico de ocupação: {hora_pico}:00h ({(ocup_horaria.max()*100):.1f}%)")

    print("\n" + "=" * 60)
    print(f"Total de registros gerados: {len(df)}")
    print(f"Período: {df['timestamp'].min()} até {df['timestamp'].max()}")
    print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulador Smart Office")
    parser.add_argument('--out', '-o', default='smart_office_data.csv', help='Arquivo CSV de saída')
    parser.add_argument('--seed', type=int, default=None, help='Seed para reproduzibilidade')
    args = parser.parse_args()

    print("Iniciando simulação de dados do Smart Office...")
    df = simular_smart_office(seed=args.seed, out_path=args.out)
    print(f"\nDados salvos em: {args.out}\n")
    gerar_relatorio_resumo(df)
    print("\nAMOSTRA DOS DADOS GERADOS (primeiras 10 linhas):")
    print(df.head(10).to_string(index=False))
    print("\n✅ Simulação concluída com sucesso!")
