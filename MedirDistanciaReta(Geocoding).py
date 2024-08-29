import pandas as pd
import requests
from geopy.distance import geodesic

def obter_coordenadas_google_maps(cidade, estado, api_key):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': f'{cidade}, {estado}, Brasil',
        'key': api_key
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if data['status'] == 'OK':
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        print(f"Erro ao obter coordenadas para {cidade}, {estado}: {data['status']}")
        return None, None

def main():
    api_key = 'sua_chave_api_google_cloud'  # Substitua pela sua chave de API do Google Maps

    # Ler o CSV com o separador correto
    df = pd.read_csv('Cidades CSV.csv', sep=';')

    # Lista das 12 cidades específicas
    cidades_especificas = [
        "Guaraniaçu"
    ]

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

            lat1, lon1 = obter_coordenadas_google_maps(city1, state1, api_key)
            lat2, lon2 = obter_coordenadas_google_maps(city2, state2, api_key)

            if lat1 and lon1 and lat2 and lon2:
                coord1 = (lat1, lon1)
                coord2 = (lat2, lon2)

                # Imprimir as coordenadas
                print(f"Coordenadas de {city1}, {state1}: {coord1}")
                print(f"Coordenadas de {city2}, {state2}: {coord2}")

                distance = geodesic(coord1, coord2).kilometers
                distancias.append({
                    'Cidade 1': city1,
                    'Estado 1': state1,
                    'Cidade 2': city2,
                    'Estado 2': state2,
                    'Distância (km)': round(distance, 2)
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
