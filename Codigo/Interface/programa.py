class Interface:
    def __init__(self):
        self.running = True

    def run(self):
        while self.running:
            self.show_menu()
            choice = input("Digite a opção desejada: ").strip()
            self.handle_choice(choice)

    def show_menu(self):
        print("\nEscolha o comando")
        print("[0] Listar vizinhos")
        print("[1] HELLO")
        print("[2] SEARCH (flooding)")
        print("[3] SEARCH (random walk)")
        print("[4] SEARCH (busca em profundidade)")
        print("[5] Estatísticas")
        print("[6] Alterar valor padrão de TTL")
        print("[9] Sair")
        
        
    def exit_program(self):
        print("Saindo...")
        self.running = False
        
    def handle_choice(self, choice):
        if choice == '0':
            print('implemente logo essa bosta')
        elif choice == '1':
            print('implemente logo essa bosta')
        elif choice == '2':
            print('implemente logo essa bosta')
        elif choice == '3':
            print('implemente logo essa bosta')
        elif choice == '4':
            print('implemente logo essa bosta')
        elif choice == '5':
            print('implemente logo essa bosta')
        elif choice == '6':
            print('implemente logo essa bosta')
        elif choice == '9':
            self.exit_program()
        else:
            print("Opção inválida. Tente novamente.")
            
if __name__ == "__main__":
    interface = Interface()
    interface.run()