import os
import hmac
import streamlit as st

st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")


APP_PASSWORD = os.getenv("APP_PASSWORD")

if not APP_PASSWORD:
    try:
        APP_PASSWORD = st.secrets["APP_PASSWORD"]
    except Exception:
        APP_PASSWORD = None

if not APP_PASSWORD:
    st.error("APP_PASSWORD not configured")
    st.stop()

def check_password(typed: str) -> bool:
    # comparação segura (evita timing attack)
    return APP_PASSWORD != "" and hmac.compare_digest(typed, APP_PASSWORD)


def logout():
    st.session_state["authenticated"] = False


def login_screen():
    st.title("🔐 Acesso ao sistema")
    st.caption("Digite a senha para continuar.")

    with st.form("login_form", clear_on_submit=False):
        pwd = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

    if submitted:
        if check_password(pwd):
            st.session_state["authenticated"] = True
            st.success("Acesso liberado!")
            st.rerun()
        else:
            st.error("Senha incorreta. Tente novamente.")


def run_app():
    # Importa so o app e chama a função principal
    import app
    if hasattr(app, "main"):
        app.main()
    else:
        st.error("O arquivo app.py precisa ter uma função main().")


def main():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        login_screen()
       
    else:
        run_app() #chama a aplicação no app.py
        # botão de sair no final da página
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.button("Sair", on_click=logout)

  


if __name__ == "__main__":
    main()
