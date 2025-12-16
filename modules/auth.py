"""
Módulo de Autenticação - Jogo do Bicho Analytics
"""
import streamlit as st

# Credenciais hardcoded
VALID_EMAIL = "marcelombarbosa.rj@gmail.com"
VALID_PASSWORD = "Farofa@123"

def check_authentication():
    """
    Verifica se o usuário está autenticado.
    Se não estiver, redireciona para a página principal de login.
    Retorna True se autenticado, False caso contrário.
    """
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.error("🔒 Acesso negado! Faça login na página principal para acessar esta seção.")
        st.info("👉 Acesse a **página inicial** no menu lateral para fazer login.")
        st.stop()
        return False
    return True

def get_current_user():
    """Retorna o e-mail do usuário logado."""
    return st.session_state.get('user_email', None)

def logout():
    """Faz logout do usuário."""
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.rerun()
