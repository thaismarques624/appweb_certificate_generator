
def main():
    import streamlit as st
    import pandas as pd
    from PyPDF2 import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    import io
    import datetime
    import zipfile


    # Configuração básica da página
    st.set_page_config(
        page_title="Gerador de Certificados – WIEPY",
        page_icon="💜",
        layout="centered"
    )

    # Logo WIE centralizado
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    st.image("imagens/logo_wie.png", width=850)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<h2 style='text-align:center;'>Gerador de Certificados – WIEPY</h2>",
        unsafe_allow_html=True
    )
    st.write("Envie o **modelo de certificado (PDF)** e uma **planilha com participantes** para gerar todos os certificados automaticamente!")

    # ---------------------------
    # UPLOADS
    # ---------------------------

    modelo_pdf = st.file_uploader("💜 Envie o modelo de certificado (PDF)", type=["pdf"])
    planilha = st.file_uploader("💜 Envie a planilha de participantes (CSV ou Excel)", type=["csv", "xlsx"])

    st.info(
        "A planilha deve conter as colunas: "
        "Nome, Evento, Participante, Local, Data, Duracao"
    )

    # ---------------------------
    # FUNÇÃO DE GERAÇÃO DE PDF
    # ---------------------------

    def gerar_certificado_streamlit(
        nome_aluno, tipo_evento, tipo_participante,
        local_evento, data_evento, duracao_evento, modelo
    ):
        """
        Gera um certificado em memória (BytesIO) usando um modelo PDF
        e os dados personalizados do participante.
        """
        pdf_reader = PdfReader(modelo)
        pdf_writer = PdfWriter()

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]

            # Canvas temporário
            packet = io.BytesIO()
            # Tamanho A4 landscape aproximado
            pagesize_per = (29.7 * inch, 21 * inch)
            c = canvas.Canvas(packet, pagesize=pagesize_per)
            c.setFont("Helvetica", 18)

            if page_num == 0:
                texto1 = (
                    f"Certifico que {nome_aluno}, participou do evento {tipo_evento} "
                    f"como {tipo_participante}, realizado {local_evento}, "
                    f"no dia {data_evento} com a duração de {duracao_evento}."
                )

                data_emissao = datetime.datetime.now().strftime("%d/%m/%Y")
                texto2 = f"Emitido em João Pessoa, {data_emissao}."
                texto = texto1 + "\n" + texto2

                font_size = 18
                frame_x = 30
                max_width = float(page.mediabox[2]) - (frame_x * 2)

                # Quebrar texto em várias linhas respeitando a largura máxima
                linhas = []
                linha_atual = ""
                for palavra in texto.split():
                    if c.stringWidth(linha_atual + " " + palavra, "Helvetica", font_size) < max_width:
                        linha_atual += (" " + palavra) if linha_atual else palavra
                    else:
                        linhas.append(linha_atual)
                        linha_atual = palavra
                if linha_atual:
                    linhas.append(linha_atual)

                # Desenhar as linhas centralizadas
                y = 400  # altura de início
                for linha in linhas:
                    largura = c.stringWidth(linha, "Helvetica", font_size)
                    x = (float(page.mediabox[2]) - largura) / 2  # centralizado
                    c.drawString(x, y, linha)
                    y -= font_size * 1.2  # espaçamento entre linhas

            c.save()
            packet.seek(0)

            new_pdf = PdfReader(packet)
            page.merge_page(new_pdf.pages[0])
            pdf_writer.add_page(page)

        # Exportar resultado para buffer
        result = io.BytesIO()
        pdf_writer.write(result)
        result.seek(0)
        return result

    # ---------------------------
    # PROCESSAMENTO DA PLANILHA
    # ---------------------------

    if st.button("🚀 Gerar Certificados"):
        if modelo_pdf is None:
            st.error("Por favor, envie o **modelo de certificado (PDF)**.")
        elif planilha is None:
            st.error("Por favor, envie a **planilha de participantes (CSV ou Excel)**.")
        else:
            # Ler a planilha
            if planilha.name.endswith(".csv"):
                df = pd.read_csv(planilha)
            else:
                df = pd.read_excel(planilha)
            
            # --- Ajuste da data ---
            df["Data"] = pd.to_datetime(df["Data"]).dt.strftime("%d/%m/%Y")

            colunas_necessarias = ["Nome", "Evento", "Participante", "Local", "Data", "Duracao"]
            if not all(col in df.columns for col in colunas_necessarias):
                st.error(
                    "A planilha deve conter as colunas: "
                    + ", ".join(colunas_necessarias)
                )
            else:
                st.success("Gerando certificados... isso pode levar alguns segundos 💜")

                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:

                    for _, row in df.iterrows():
                        nome = str(row["Nome"])
                        evento = str(row["Evento"])
                        participante = str(row["Participante"])
                        local = str(row["Local"])
                        data = str(row["Data"])
                        duracao = str(row["Duracao"])

                        certificado = gerar_certificado_streamlit(
                            nome, evento, participante, local, data, duracao, modelo_pdf
                        )

                        safe_nome = nome.replace(" ", "_")
                        zipf.writestr(f"certificado_{safe_nome}.pdf", certificado.getvalue())

                zip_buffer.seek(0)

                st.download_button(
                    label="📥 Baixar Todos os Certificados (ZIP)",
                    data=zip_buffer,
                    file_name="certificados_wiepy.zip",
                    mime="application/zip"
                )

                st.success("Todos os certificados foram gerados com sucesso! 🎓")
