import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class ClientManager:
    def __init__(self, db_name="clients.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    cpf TEXT NOT NULL UNIQUE,
                    rg TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE
                )
            ''')

    def add_client(self, name, address, phone, cpf, rg, email):
        try:
            with self.conn:
                self.conn.execute('''
                    INSERT INTO clients (name, address, phone, cpf, rg, email) 
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (name, address, phone, cpf, rg, email))
            return True
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Erro", str(e))
            return False

    def list_clients(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM clients')
        return cursor.fetchall()

    def search_client(self, client_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM clients WHERE id = ?', (client_id,))
        return cursor.fetchone()

    def delete_client(self, client_id):
        with self.conn:
            self.conn.execute('DELETE FROM clients WHERE id = ?', (client_id,))

    def __del__(self):
        self.conn.close()

class ClientApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cadastro de Clientes")
        self.geometry("600x400")
        self.manager = ClientManager()

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(padx=10, pady=10, fill=tk.X, expand=True)

        # Nome
        ttk.Label(frame, text="Nome:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(frame)
        self.name_entry.grid(row=0, column=1, pady=5)

        # Endereço
        ttk.Label(frame, text="Endereço:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.address_entry = ttk.Entry(frame)
        self.address_entry.grid(row=1, column=1, pady=5)

        # Telefone
        ttk.Label(frame, text="Telefone:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.phone_entry = ttk.Entry(frame)
        self.phone_entry.grid(row=2, column=1, pady=5)

        # CPF
        ttk.Label(frame, text="CPF3:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.cpf_entry = ttk.Entry(frame)
        self.cpf_entry.grid(row=3, column=1, pady=5)

        # RG
        ttk.Label(frame, text="RG:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.rg_entry = ttk.Entry(frame)
        self.rg_entry.grid(row=4, column=1, pady=5)

        # Email
        ttk.Label(frame, text="Email:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.email_entry = ttk.Entry(frame)
        self.email_entry.grid(row=5, column=1, pady=5)

        # Botões
        ttk.Button(frame, text="Adicionar Cliente", command=self.add_client).grid(row=6, column=0, pady=10)
        ttk.Button(frame, text="Listar Clientes", command=self.list_clients).grid(row=6, column=1, pady=10)
        ttk.Button(frame, text="Gerar Relatório PDF", command=self.generate_pdf_report).grid(row=6, column=2, pady=10)
        ttk.Button(frame, text="Abrir Relatório PDF", command=self.open_pdf_report).grid(row=6, column=3, pady=10)

        # Lista de Clientes
        self.client_list = ttk.Treeview(self, columns=("ID", "Nome", "Endereço", "Telefone", "CPF", "RG", "Email"), show="headings")
        self.client_list.heading("ID", text="ID")
        self.client_list.heading("Nome", text="Nome")
        self.client_list.heading("Endereço", text="Endereço")
        self.client_list.heading("Telefone", text="Telefone")
        self.client_list.heading("CPF", text="CPF")
        self.client_list.heading("RG", text="RG")
        self.client_list.heading("Email", text="Email")
        self.client_list.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.client_list.bind("<Delete>", self.delete_client)

    def add_client(self):
        name = self.name_entry.get()
        address = self.address_entry.get()
        phone = self.phone_entry.get()
        cpf = self.cpf_entry.get()
        rg = self.rg_entry.get()
        email = self.email_entry.get()

        if self.manager.add_client(name, address, phone, cpf, rg, email):
            messagebox.showinfo("Sucesso", "Cliente adicionado com sucesso.")
            self.clear_entries()
            self.list_clients()

    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.cpf_entry.delete(0, tk.END)
        self.rg_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)

    def list_clients(self):
        for row in self.client_list.get_children():
            self.client_list.delete(row)

        clients = self.manager.list_clients()
        for client in clients:
            self.client_list.insert('', tk.END, values=client)

    def delete_client(self, event):
        selected_item = self.client_list.selection()[0]
        client_id = self.client_list.item(selected_item)["values"][0]
        self.manager.delete_client(client_id)
        self.client_list.delete(selected_item)
        messagebox.showinfo("Sucesso", "Cliente deletado com sucesso.")

    def generate_pdf_report(self):
        clients = self.manager.list_clients()
        c = canvas.Canvas("relatorio_clientes.pdf", pagesize=letter)
        width, height = letter
        c.drawString(30, height - 30, "Relatório de Clientes")
        y = height - 60

        for client in clients:
            text = f"ID: {client[0]}, Nome: {client[1]}, Endereço: {client[2]}, Telefone: {client[3]}, CPF: {client[4]}, RG: {client[5]}, Email: {client[6]}"
            c.drawString(30, y, text)
            y -= 20
            if y < 30:
                c.showPage()
                y = height - 30

        c.save()
        messagebox.showinfo("Sucesso", "Relatório PDF gerado com sucesso.")

    def open_pdf_report(self):
        try:
            os.startfile("relatorio_clientes.pdf")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o relatório PDF: {str(e)}")

if __name__ == "__main__":
    app = ClientApp()
    app.mainloop()
