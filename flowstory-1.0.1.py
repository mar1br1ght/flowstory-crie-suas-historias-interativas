import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import time
import os
from datetime import datetime

class FlowStoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FlowStory")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f5f0ff')
        
        # Estado da aplicação
        self.current_project = None
        self.user_logged_in = False
        self.current_user = None
        self.auto_save_enabled = True
        self.last_save = time.time()
        
        # Dados da rede social
        self.users = {}
        self.stories = []
        self.jams = []
        self.wikis = []
        
        # Configurar estilo
        self.setup_styles()
        
        # Mostrar menu principal primeiro
        self.show_main_menu()
        
        # Configurar atalhos de teclado
        self.setup_keyboard_shortcuts()
        
        # Iniciar salvamento automático
        self.root.after(15000, self.auto_save)
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        colors = {
            'lilac': '#e6e6fa',
            'pastel_orange': '#ffd8b1',
            'pastel_yellow': '#fffacd',
            'pastel_pink': '#ffd1dc',
            'mint_green': '#b5e7a0',
            'light_lilac': '#f5f0ff',
            'trash_red': '#ffb3b3',
            'deep_lilac': '#d8bfd8'
        }
        
        style.configure('Main.TFrame', background=colors['light_lilac'])
        style.configure('Menu.TButton', background=colors['lilac'], foreground='#333333')
        style.configure('Bubble.TButton', background=colors['pastel_orange'], foreground='#333333')
        style.configure('Tab.TFrame', background=colors['lilac'])
        style.configure('Trash.TButton', background=colors['trash_red'], foreground='#333333')
        style.configure('Social.TButton', background=colors['deep_lilac'], foreground='#333333')
        style.configure('Title.TLabel', background=colors['light_lilac'], foreground='#6a5acd', font=('Arial', 16, 'bold'))
    
    def show_main_menu(self):
        # Limpar tela anterior
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Frame principal do menu
        menu_frame = ttk.Frame(self.root, style='Main.TFrame')
        menu_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        
        # Título
        title_label = ttk.Label(menu_frame, text="🌸 FlowStory 🌸", style='Title.TLabel')
        title_label.pack(pady=30)
        
        # Subtítulo
        subtitle_label = ttk.Label(menu_frame, text="Editor Visual de Histórias Interativas", 
                                  background='#f5f0ff', font=('Arial', 12))
        subtitle_label.pack(pady=10)
        
        # Frame dos botões principais
        buttons_frame = ttk.Frame(menu_frame, style='Main.TFrame')
        buttons_frame.pack(pady=30)
        
        # Botões do menu principal
        menu_buttons = [
            ("🎮 Iniciar Nova História", self.start_new_story),
            ("🎬 Nova Websérie", self.start_new_webseries),
            ("🌊 Entrar na Flow", self.open_flow_social),
            ("⚙️ Configurações", self.open_settings),
            ("❌ Sair", self.root.quit)
        ]
        
        for text, command in menu_buttons:
            btn = ttk.Button(buttons_frame, text=text, command=command, 
                           style='Social.TButton', width=25)
            btn.pack(pady=10)
        
        # Status do usuário
        self.user_status_label = ttk.Label(menu_frame, text="Visitante - Faça login na Flow", 
                                          background='#f5f0ff', font=('Arial', 10))
        self.user_status_label.pack(pady=20)
        
        # Atualizar status do usuário
        self.update_user_status()
    
    def update_user_status(self):
        if self.user_logged_in and self.current_user:
            status_text = f"👤 {self.current_user['nick']} - Conectada na Flow"
            self.user_status_label.config(text=status_text)
        else:
            self.user_status_label.config(text="Visitante - Faça login na Flow")
    
    def start_new_story(self):
        self.setup_main_interface()
        self.new_story()
    
    def start_new_webseries(self):
        self.setup_main_interface()
        self.new_webseries()
    
    def open_flow_social(self):
        if not self.user_logged_in:
            self.open_login()
        else:
            self.show_flow_social()
    
    def show_flow_social(self):
        # Limpar tela anterior
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Frame principal da rede social
        social_frame = ttk.Frame(self.root, style='Main.TFrame')
        social_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Barra superior
        top_bar = ttk.Frame(social_frame, style='Main.TFrame')
        top_bar.pack(fill=tk.X, pady=10)
        
        ttk.Button(top_bar, text="← Voltar ao Menu", 
                  command=self.show_main_menu, style='Menu.TButton').pack(side=tk.LEFT)
        
        ttk.Label(top_bar, text="🌊 Flow - Rede Social", 
                 style='Title.TLabel').pack(side=tk.LEFT, padx=20)
        
        ttk.Button(top_bar, text="Minha Banca", 
                  command=self.show_my_stand, style='Social.TButton').pack(side=tk.RIGHT, padx=5)
        ttk.Button(top_bar, text="Explorar", 
                  command=self.show_explore, style='Social.TButton').pack(side=tk.RIGHT, padx=5)
        
        # Área principal
        self.social_notebook = ttk.Notebook(social_frame)
        self.social_notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Abas da rede social
        self.setup_my_stand_tab()
        self.setup_explore_tab()
        self.setup_chat_tab()
        self.setup_jams_tab()
        
        # Mostrar aba inicial
        self.social_notebook.select(0)
    
    def setup_my_stand_tab(self):
        my_stand_frame = ttk.Frame(self.social_notebook)
        self.social_notebook.add(my_stand_frame, text="🏪 Minha Banca")
        
        # Cabeçalho da banca
        header_frame = ttk.Frame(my_stand_frame, style='Main.TFrame')
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        if self.current_user:
            ttk.Label(header_frame, text=f"👤 {self.current_user['nick']}", 
                     font=('Arial', 14, 'bold')).pack(side=tk.LEFT)
            
            ttk.Button(header_frame, text="Editar Perfil", 
                      command=self.edit_profile).pack(side=tk.RIGHT)
        
        # Área de atualizações
        update_frame = ttk.LabelFrame(my_stand_frame, text="📢 Atualizações (max 250 caracteres)")
        update_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.update_text = tk.Text(update_frame, height=3, width=50)
        self.update_text.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(update_frame, text="Publicar", 
                  command=self.publish_update).pack(pady=5)
        
        # Minhas histórias
        stories_frame = ttk.LabelFrame(my_stand_frame, text="📚 Minhas Histórias")
        stories_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Lista de histórias (simulada)
        stories_list = ttk.Frame(stories_frame)
        stories_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        sample_stories = ["Aventura na Floresta Encantada", "Mistério no Castelo", "Romance de Verão"]
        
        for story in sample_stories:
            story_frame = ttk.Frame(stories_list)
            story_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(story_frame, text=story).pack(side=tk.LEFT)
            ttk.Button(story_frame, text="Abrir", 
                      command=lambda s=story: self.open_story(s)).pack(side=tk.RIGHT, padx=5)
            ttk.Button(story_frame, text="Compartilhar", 
                      command=lambda s=story: self.share_story(s)).pack(side=tk.RIGHT, padx=5)
    
    def setup_explore_tab(self):
        explore_frame = ttk.Frame(self.social_notebook)
        self.social_notebook.add(explore_frame, text="🔍 Explorar")
        
        # Barra de pesquisa
        search_frame = ttk.Frame(explore_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(search_frame, text="Pesquisar:").pack(side=tk.LEFT)
        explore_search = ttk.Entry(search_frame, width=30)
        explore_search.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Buscar", 
                  command=lambda: self.search_content(explore_search.get())).pack(side=tk.LEFT)
        
        # Categorias
        categories_frame = ttk.LabelFrame(explore_frame, text="📂 Categorias")
        categories_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        categories = [
            ("🧙 Histórias de Fantasia", self.show_fantasy_stories),
            ("💕 Romances", self.show_romance_stories),
            ("🔍 Mistério", self.show_mystery_stories),
            ("🚀 Ficção Científica", self.show_scifi_stories),
            ("📚 Fanfics", self.show_fanfics),
            ("❓ Quizzes", self.show_quizzes),
            ("🌐 Wikis", self.show_wikis)
        ]
        
        for text, command in categories:
            btn = ttk.Button(categories_frame, text=text, command=command, style='Bubble.TButton')
            btn.pack(fill=tk.X, padx=5, pady=2)
    
    def setup_chat_tab(self):
        chat_frame = ttk.Frame(self.social_notebook)
        self.social_notebook.add(chat_frame, text="💬 Bate-papo")
        
        ttk.Label(chat_frame, text="💬 Sala de Bate-papo da Flow", 
                 font=('Arial', 12, 'bold')).pack(pady=20)
        
        # Área de mensagens
        messages_frame = ttk.LabelFrame(chat_frame, text="Mensagens")
        messages_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.chat_display = tk.Text(messages_frame, height=15, state=tk.DISABLED)
        chat_scrollbar = ttk.Scrollbar(messages_frame, command=self.chat_display.yview)
        self.chat_display.configure(yscrollcommand=chat_scrollbar.set)
        
        self.chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Entrada de mensagem
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.message_entry = ttk.Entry(input_frame)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.message_entry.bind('<Return>', self.send_chat_message)
        
        ttk.Button(input_frame, text="Enviar", 
                  command=self.send_chat_message).pack(side=tk.RIGHT)
        
        # Adicionar algumas mensagens de exemplo
        self.add_sample_messages()
    
    def setup_jams_tab(self):
        jams_frame = ttk.Frame(self.social_notebook)
        self.social_notebook.add(jams_frame, text="🎉 Jams")
        
        ttk.Label(jams_frame, text="🎉 Jams e Eventos da Flow", 
                 font=('Arial', 12, 'bold')).pack(pady=20)
        
        # Lista de jams
        jams_list = [
            {"name": "Jam de Verão 2024", "theme": "Férias Inesquecíveis", "date": "01-15/07/2024"},
            {"name": "Halloween Jam", "theme": "Terror e Mistério", "date": "20-31/10/2024"},
            {"name": "Natal Mágico", "theme": "Histórias de Natal", "date": "01-25/12/2024"}
        ]
        
        for jam in jams_list:
            jam_frame = ttk.LabelFrame(jams_frame, text=jam["name"])
            jam_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(jam_frame, text=f"Tema: {jam['theme']}").pack(anchor=tk.W)
            ttk.Label(jam_frame, text=f"Período: {jam['date']}").pack(anchor=tk.W)
            
            ttk.Button(jam_frame, text="Participar", 
                      command=lambda j=jam: self.join_jam(j)).pack(pady=5)
    
    def add_sample_messages(self):
        messages = [
            ("Florzinha", "Alguém participando da Jam de Verão?"),
            ("Criativa23", "Estou amando as novas histórias de fantasia!"),
            ("Sonhadora", "Preciso de ajuda com transições no FlowStory, alguém pode ajudar?"),
            ("ArtistaFlow", "Acabei de publicar minha nova websérie! 🎬")
        ]
        
        for user, message in messages:
            self.add_message_to_chat(user, message)
    
    def add_message_to_chat(self, user, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{user}: {message}\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def send_chat_message(self, event=None):
        message = self.message_entry.get().strip()
        if message and self.current_user:
            self.add_message_to_chat(self.current_user['nick'], message)
            self.message_entry.delete(0, tk.END)
    
    def show_my_stand(self):
        self.social_notebook.select(0)
    
    def show_explore(self):
        self.social_notebook.select(1)
    
    def edit_profile(self):
        profile_window = tk.Toplevel(self.root)
        profile_window.title("Editar Perfil")
        profile_window.geometry("400x300")
        
        ttk.Label(profile_window, text="Editar Perfil", font=('Arial', 14, 'bold')).pack(pady=10)
        
        ttk.Label(profile_window, text="Nick:").pack(pady=5)
        nick_entry = ttk.Entry(profile_window, width=30)
        nick_entry.insert(0, self.current_user['nick'])
        nick_entry.pack(pady=5)
        
        ttk.Label(profile_window, text="Bio:").pack(pady=5)
        bio_text = tk.Text(profile_window, height=4, width=40)
        bio_text.pack(pady=5)
        
        ttk.Button(profile_window, text="Salvar", 
                  command=lambda: self.save_profile(nick_entry.get(), bio_text.get(1.0, tk.END), profile_window)).pack(pady=10)
    
    def save_profile(self, nick, bio, window):
        if nick:
            self.current_user['nick'] = nick
            self.current_user['bio'] = bio.strip()
            self.update_user_status()
            messagebox.showinfo("Sucesso", "Perfil atualizado!")
            window.destroy()
    
    def publish_update(self):
        update_text = self.update_text.get(1.0, tk.END).strip()
        if update_text and len(update_text) <= 250:
            # Simular publicação
            messagebox.showinfo("Sucesso", "Atualização publicada!")
            self.update_text.delete(1.0, tk.END)
        elif len(update_text) > 250:
            messagebox.showerror("Erro", "Máximo de 250 caracteres!")
    
    def open_story(self, story_name):
        messagebox.showinfo("Abrir História", f"Abrindo: {story_name}")
    
    def share_story(self, story_name):
        messagebox.showinfo("Compartilhar", f"Compartilhando: {story_name}")
    
    def search_content(self, query):
        if query:
            messagebox.showinfo("Pesquisar", f"Buscando: {query}")
    
    def show_fantasy_stories(self):
        self.show_category_stories("Fantasia")
    
    def show_romance_stories(self):
        self.show_category_stories("Romance")
    
    def show_mystery_stories(self):
        self.show_category_stories("Mistério")
    
    def show_scifi_stories(self):
        self.show_category_stories("Ficção Científica")
    
    def show_fanfics(self):
        messagebox.showinfo("Fanfics", "Explorando Fanfics")
    
    def show_quizzes(self):
        messagebox.showinfo("Quizzes", "Explorando Quizzes")
    
    def show_wikis(self):
        messagebox.showinfo("Wikis", "Explorando Wikis")
    
    def show_category_stories(self, category):
        messagebox.showinfo(category, f"Explorando histórias de {category}")
    
    def join_jam(self, jam):
        messagebox.showinfo("Participar", f"Participando da jam: {jam['name']}")
    
    def setup_keyboard_shortcuts(self):
        self.root.bind('<Control-z>', self.undo)
        self.root.bind('<Control-y>', self.redo)
        self.root.bind('<Control-s>', self.manual_save)
        self.root.bind('<Delete>', self.delete_selected)
        self.root.bind('<KeyPress-r>', self.quick_export)
        self.root.bind('<KeyPress-a>', self.show_tabs)
        self.root.bind('<Escape>', self.close_app)
        self.root.bind('<BackSpace>', self.delete_selected)
        self.root.bind('<F2>', self.focus_text_editor)
        self.root.bind('<F1>', lambda e: self.show_main_menu())
    
    # ... (os métodos do editor permanecem os mesmos, mas vou incluir os principais)
    
    def setup_main_interface(self):
        # Limpar tela anterior
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Frame principal
        main_frame = ttk.Frame(self.root, style='Main.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Barra de opções superior
        self.setup_top_bar(main_frame)
        
        # Área de trabalho principal
        self.setup_work_area(main_frame)
        
        # Barra de status
        self.setup_status_bar(main_frame)
    
    def setup_top_bar(self, parent):
        top_frame = ttk.Frame(parent, style='Main.TFrame')
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Botões da barra superior
        buttons = [
            ("🏠 Menu", self.show_main_menu),
            ("🌊 Flow", self.open_flow_social),
            ("Nova História", self.new_story),
            ("Nova Websérie", self.new_webseries),
            ("Configuração", self.open_settings),
            ("Preview", self.preview_project),
            ("Exportar", self.export_project)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(top_frame, text=text, command=command, style='Menu.TButton')
            btn.pack(side=tk.LEFT, padx=5)
    
    def open_login(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("Login - FlowStory")
        login_window.geometry("300x250")
        
        ttk.Label(login_window, text="Login na Flow", font=('Arial', 14, 'bold')).pack(pady=10)
        
        ttk.Label(login_window, text="Nick ou Email:").pack(pady=5)
        nick_entry = ttk.Entry(login_window, width=30)
        nick_entry.pack(pady=5)
        
        ttk.Label(login_window, text="Senha ou Código:").pack(pady=5)
        password_entry = ttk.Entry(login_window, width=30, show="*")
        password_entry.pack(pady=5)
        
        button_frame = ttk.Frame(login_window)
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="Entrar", 
                  command=lambda: self.do_login(nick_entry.get(), password_entry.get(), login_window)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Convidar-se", 
                  command=lambda: self.show_invite(login_window)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", 
                  command=login_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def show_invite(self, parent_window):
        parent_window.destroy()
        self.invite_user()
    
    def do_login(self, nick, password, window):
        if nick and password:
            # Simular login bem-sucedido
            self.user_logged_in = True
            self.current_user = {
                'nick': nick,
                'email': f"{nick}@flow.com",
                'bio': "Novo usuário da Flow!",
                'joined': datetime.now().strftime("%d/%m/%Y")
            }
            self.update_user_status()
            messagebox.showinfo("Bem-vinda!", f"Login realizado com sucesso!\nBem-vinda de volta, {nick}!")
            window.destroy()
            
            # Se veio do menu principal, abrir a rede social
            if hasattr(self, 'social_notebook'):
                self.show_flow_social()
        else:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos")
    
    def invite_user(self):
        invite_window = tk.Toplevel(self.root)
        invite_window.title("Convidar-se - FlowStory")
        invite_window.geometry("350x300")
        
        ttk.Label(invite_window, text="Junte-se à Flow!", font=('Arial', 14, 'bold')).pack(pady=10)
        
        ttk.Label(invite_window, text="Nick desejado:").pack(pady=5)
        nick_entry = ttk.Entry(invite_window, width=30)
        nick_entry.pack(pady=5)
        
        ttk.Label(invite_window, text="Senha:").pack(pady=5)
        password_entry = ttk.Entry(invite_window, width=30, show="*")
        password_entry.pack(pady=5)
        
        ttk.Label(invite_window, text="Email:").pack(pady=5)
        email_entry = ttk.Entry(invite_window, width=30)
        email_entry.pack(pady=5)
        
        button_frame = ttk.Frame(invite_window)
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="Criar Conta", 
                  command=lambda: self.create_account(nick_entry.get(), password_entry.get(), email_entry.get(), invite_window)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Voltar", 
                  command=invite_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def create_account(self, nick, password, email, window):
        if nick and password and email:
            self.user_logged_in = True
            self.current_user = {
                'nick': nick,
                'email': email,
                'bio': "Novo usuário da Flow!",
                'joined': datetime.now().strftime("%d/%m/%Y")
            }
            self.update_user_status()
            
            # Simular envio de código
            code = "FLOW" + str(hash(nick + email))[-4:].upper()
            
            messagebox.showinfo("Sucesso!", 
                              f"Conta criada com sucesso!\n\n"
                              f"Bem-vinda à Flow, {nick}!\n\n"
                              f"Seu código de entrada único:\n{code}\n\n"
                              f"Este código foi enviado para: {email}")
            window.destroy()
            
            # Mostrar rede social após criar conta
            self.show_flow_social()
        else:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos")
    
    # ... (os métodos restantes do editor permanecem iguais)
    def setup_work_area(self, parent):
        work_frame = ttk.Frame(parent, style='Main.TFrame')
        work_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.setup_bubble_panel(work_frame)
        self.setup_workspace(work_frame)
        self.setup_right_panel(work_frame)
    
    def setup_bubble_panel(self, parent):
        bubble_frame = ttk.LabelFrame(parent, text="Bolhas", style='Tab.TFrame')
        bubble_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        self.bubble_notebook = ttk.Notebook(bubble_frame)
        self.bubble_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        categories = [
            ("Esqueleto", ["Se", "Contexto", "Então", "Senão"]),
            ("Aparência", ["Mover Personagem", "Mudar Foco", "Cenário", "Esconder Personagem"]),
            ("Bolhas Filhas", ["Personagem", "Cenário", "Mudar Expressão", "Trazer Personagem"]),
            ("Cenas", ["Novo Capítulo", "Criar Rota", "Diálogo"]),
            ("Transições", ["Tempo de Slide", "Transição Súbita", "Mudar Expressão", "Cena"]),
            ("Fim", ["Parar Tudo"])
        ]
        
        for category_name, bubbles in categories:
            frame = ttk.Frame(self.bubble_notebook)
            self.bubble_notebook.add(frame, text=category_name)
            
            for bubble in bubbles:
                btn = ttk.Button(frame, text=bubble, style='Bubble.TButton',
                                command=lambda b=bubble: self.add_bubble_to_workspace(b))
                btn.pack(fill=tk.X, padx=5, pady=2)
    
    # ... (continuam todos os outros métodos do editor: setup_workspace, setup_right_panel, etc.)

    # Métodos do editor que precisam ser incluídos para funcionamento
    def setup_workspace(self, parent):
        workspace_frame = ttk.LabelFrame(parent, text="Mesa de Trabalho")
        workspace_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.workspace_canvas = tk.Canvas(workspace_frame, bg='white', scrollregion=(0, 0, 1000, 1000))
        
        v_scrollbar = ttk.Scrollbar(workspace_frame, orient=tk.VERTICAL, command=self.workspace_canvas.yview)
        h_scrollbar = ttk.Scrollbar(workspace_frame, orient=tk.HORIZONTAL, command=self.workspace_canvas.xview)
        
        self.workspace_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.workspace_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.workspace_canvas.bind("<ButtonPress-1>", self.on_canvas_click)
        self.workspace_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.workspace_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        self.dragged_item = None
        self.selected_bubble = None
        self.bubbles = []
        self.history = []
        self.history_position = -1
    
    def setup_right_panel(self, parent):
        right_frame = ttk.Frame(parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        self.setup_text_editor(right_frame)
        self.setup_trash_area(right_frame)
    
    def setup_text_editor(self, parent):
        editor_frame = ttk.LabelFrame(parent, text="Editor de Texto de Bolhas")
        editor_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.text_editor = tk.Text(editor_frame, width=30, height=15, wrap=tk.WORD)
        text_scrollbar = ttk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=self.text_editor.yview)
        self.text_editor.configure(yscrollcommand=text_scrollbar.set)
        
        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        button_frame = ttk.Frame(editor_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Aplicar", command=self.apply_text_changes).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Limpar", command=self.clear_text_editor).pack(side=tk.LEFT, padx=2)
    
    def setup_trash_area(self, parent):
        trash_frame = ttk.LabelFrame(parent, text="Lixeira")
        trash_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.trash_button = ttk.Button(
            trash_frame, 
            text="🗑️\nLixeira\n(Arraste bolhas aqui\nou pressione Delete)",
            style='Trash.TButton',
            command=self.show_trash_contents
        )
        self.trash_button.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.trash_button.bind("<ButtonRelease-1>", self.drop_on_trash)
        
        self.deleted_bubbles = []
    
    def setup_status_bar(self, parent):
        status_frame = ttk.Frame(parent, style='Main.TFrame')
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Pronto para começar")
        self.status_label.pack(side=tk.LEFT)
        
        self.save_indicator = ttk.Label(status_frame, text="✓ Auto-salvo")
        self.save_indicator.pack(side=tk.RIGHT)
    
    # ... (continuam todos os outros métodos do editor anterior)

    # Métodos essenciais para evitar erros
    def add_bubble_to_workspace(self, bubble_type):
        # Implementação básica para evitar erro
        x, y = 50, 50
        bubble_id = self.workspace_canvas.create_oval(x, y, x+100, y+60, fill='#ffd8b1')
        text_id = self.workspace_canvas.create_text(x+50, y+30, text=bubble_type)
        
        bubble_data = {'id': bubble_id, 'text_id': text_id, 'type': bubble_type}
        self.bubbles.append(bubble_data)
        self.status_label.config(text=f"Bolha '{bubble_type}' adicionada")
    
    def new_story(self):
        self.current_project = {"type": "story"}
        self.workspace_canvas.delete("all")
        self.bubbles = []
        self.status_label.config(text="Nova história interativa criada")
    
    def new_webseries(self):
        self.current_project = {"type": "webseries"}
        self.workspace_canvas.delete("all")
        self.bubbles = []
        self.status_label.config(text="Nova websérie criada")
    
    def open_settings(self):
        messagebox.showinfo("Configurações", "Menu de configurações")
    
    def preview_project(self):
        messagebox.showinfo("Preview", "Visualização do projeto")
    
    def export_project(self):
        messagebox.showinfo("Exportar", "Menu de exportação")
    
    def undo(self, event=None): pass
    def redo(self, event=None): pass
    def manual_save(self, event=None): pass
    def delete_selected(self, event=None): pass
    def quick_export(self, event=None): pass
    def show_tabs(self, event=None): pass
    def close_app(self, event=None): 
        if messagebox.askokcancel("Sair", "Deseja realmente sair?"):
            self.root.quit()
    def focus_text_editor(self, event=None): pass
    def on_canvas_click(self, event): pass
    def on_canvas_drag(self, event): pass
    def on_canvas_release(self, event): pass
    def drop_on_trash(self, event): pass
    def show_trash_contents(self): pass
    def apply_text_changes(self): pass
    def clear_text_editor(self): pass
    def auto_save(self): 
        self.root.after(15000, self.auto_save)

def main():
    root = tk.Tk()
    app = FlowStoryApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
