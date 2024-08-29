import pandas as pd
import requests

def obter_distancia_rota_google_maps(origem, destino, api_key):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        'origins': origem,
        'destinations': destino,
        'key': api_key,
        'mode': 'driving',  # Modo de transporte: pode ser driving, walking, bicycling, etc.
        'language': 'pt-BR'
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if data['status'] == 'OK':
        if data['rows'][0]['elements'][0]['status'] == 'OK':
            distancia_metros = data['rows'][0]['elements'][0]['distance']['value']
            distancia_km = distancia_metros / 1000.0
            return round(distancia_km, 2)
        else:
            print(f"Erro ao obter a distância entre {origem} e {destino}: {data['rows'][0]['elements'][0]['status']}")
            return None
    else:
        print(f"Erro na solicitação à API: {data['status']}")
        return None

def main():
    api_key = 'AIzaSyAUlO7WPk7PR2cat3JTl3UerhBF0V5y-AM'  # Substitua pela sua chave de API do Google Maps

    # Ler o CSV com o separador correto
    df = pd.read_csv('Cidades CSV.csv', sep=';')

    # Lista das 12 cidades específicas
    cidades_especificas = [
        "Guaraniaçu"
    ]
    
    #   "Toledo","Verê", "Cascavel", "Guaraniaçu", "Laranjeiras do Sul", 
    #   "Santa Tereza do Oeste", "Capitão Leônidas Marques", "Vera Cruz do Oeste", 
    #   "Ouro Verde do Oeste", "Nova Santa Rosa", "Vitorino", "Salto do Lontra"

    # Filtrar o DataFrame para obter apenas as cidades específicas
    df_especificas = df[df['Cidade'].isin(cidades_especificas)]

    distancias = []
    chunk_size = 100  # Define o tamanho do bloco para a geração do CSV
    parcial_filename = 'distancias_parcial.csv'

    for i in range(len(df_especificas)):
        for j in range(len(df)):
            if df_especificas.iloc[i]['Cidade'] == df.iloc[j]['Cidade']:  # Evitar comparação da cidade com ela mesma
                continue

            row1 = df_especificas.iloc[i]
            row2 = df.iloc[j]

            city1, state1 = row1['Cidade'], row1['Estado']
            city2, state2 = row2['Cidade'], row2['Estado']

            origem = f"{city1}, {state1}, Brasil"
            destino = f"{city2}, {state2}, Brasil"

            distancia_km = obter_distancia_rota_google_maps(origem, destino, api_key)

            if distancia_km:
                distancias.append({
                    'Cidade 1': city1,
                    'Estado 1': state1,
                    'Cidade 2': city2,
                    'Estado 2': state2,
                    'Distância (km)': distancia_km
                })

                # Salvamento intermediário a cada chunk_size registros
                if len(distancias) % chunk_size == 0:
                    df_intermediario = pd.DataFrame(distancias[-chunk_size:])
                    if len(distancias) == chunk_size:
                        df_intermediario.to_csv(parcial_filename, mode='w', index=False, sep=';', header=True)
                    else:
                        df_intermediario.to_csv(parcial_filename, mode='a', index=False, sep=';', header=False)
                    
                    # Exibir feedback no console
                    print(f"{len(distancias)} distâncias processadas...")

    # Salvar o CSV final
    df_distancias = pd.DataFrame(distancias)
    df_distancias.to_csv('distancias_cidades.csv', index=False, sep=';')
    print("Arquivo distancias_cidades.csv criado com sucesso!")

if __name__ == "__main__":
    main()
