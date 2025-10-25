import requests
import pandas as pd
import time

class Dados:
    def __init__(self):
        self.url = 'http://ec2-52-67-119-247.sa-east-1.compute.amazonaws.com:8000'
        self.auth = {
          "password": "4w9f@D39fkkO",
          "username": "kaizen-poke"
        }
        self.status = None
        self.headers = None
        self.pokemons_data = pd.DataFrame()
        self.pokemons = pd.DataFrame()
        self.combats = pd.DataFrame()

    def get_token(self):
        response = requests.post(f'{self.url}/login', json=self.auth)

        if response.status_code == 200:
            token = response.json().get('access_token')
            self.headers = {"Authorization": f"Bearer {token}"}
            print("Token obtido com sucesso!")
        else:
            print(f"Failed to obtain token")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")

    def get_status(self):
        response = requests.get(f'{self.url}/health', headers=self.headers)
        if response.status_code == 200:
            self.status = response.json().get('status')
        else:
            print(f"Failed to get status ({response.status_code})")

    def get_pokemons_ids(self):
        for page in range(1, 17):
            response = requests.get(f'{self.url}/pokemon?page={page}&per_page=50', headers=self.headers, timeout=10)
            try:
                for pokemon in response.json()['pokemons']:
                    data = pd.DataFrame([pokemon])
                    self.pokemons = pd.concat([self.pokemons, data], ignore_index=True)
                    self.get_pokemons_attributes(pokemon['id'])
            except:
                print(f"Failed to get pokemons on page")
                            
    def get_pokemons_attributes(self, id):
        try:
            response = requests.get(f'{self.url}/pokemon/{id}', headers=self.headers,timeout=10)
        except requests.exceptions.Timeout:
            print(f"Request timed out for Pokémon ID {id} tentando de novo...")
            time.sleep(2)
            response = requests.get(f'{self.url}/pokemon/{id}', headers=self.headers,timeout=10)
            if response.status_code != 200:
                print(f"Failed again to get attributes for Pokémon ID {id} ({response.status_code})")
                return
            else:
                print(f"Success on retry for Pokémon ID {id}")

        if response.status_code == 200:
            data = response.json()
            df_aux = pd.DataFrame([data])
            self.pokemons_data = pd.concat([self.pokemons_data, df_aux], ignore_index=True)
        else:
            print(f"Failed to get attributes for Pokémon ID {id} ({response.status_code})")

    def get_combats(self):
        for page in range(1, 501):
            try:
                response = requests.get(f'{self.url}/combats?page={page}&per_page=100', headers=self.headers, timeout=10)
            except requests.exceptions.Timeout:
                print(f"Request timed out for combats page {page} tentando de novo...")
                time.sleep(3)
                response = requests.get(f'{self.url}/combats?page={page}&per_page=100', headers=self.headers, timeout=10)
                if response.status_code != 200:
                    print(f"Failed again to get combats on page {page} ({response.status_code})")
                    return
                else:
                    print(f"Success on retry for combats page {page}")

            if response.status_code == 200:
                try:
                    for combat in response.json()['combats']:
                        data = pd.DataFrame([combat])
                        self.combats = pd.concat([self.combats, data], ignore_index=True)
                except:
                    print(f"Failed to get combats on page")

    def cria_dados(self):
        self.get_token()
        if not self.headers:
            raise Exception("Não foi possível obter o token de autenticação")

        self.get_status()
        
        if self.status == 'ok':
            print("API funcionando, continuando...")
        else:
            raise Exception("API não está funcionando")
        
        self.get_pokemons_ids()

        self.pokemons.to_csv('pokemons.csv', index=False)
        self.pokemons_data.to_csv('pokemons_data.csv', index=False)
        
        self.get_combats()

        self.combats.to_csv('combats.csv', index=False)

def main():
    dados_pokemons = Dados()
    dados_pokemons.cria_dados()

if __name__ == "__main__":
    main()