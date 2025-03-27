from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
import mysql.connector

# Configurar conexão com o banco de dados
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",
    database="bot"
)

# Definindo as etapas do processo
NOME, CPF, CAMISA = range(3)

# Comando inicial
async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Olá! Por favor, envie o nome da pessoa.")
    return NOME

# Função para capturar o nome
async def get_nome(update: Update, context: CallbackContext) -> int:
    context.user_data['nome'] = update.message.text
    await update.message.reply_text("Agora envie o CPF:")
    return CPF

# Função para capturar o CPF
async def get_cpf(update: Update, context: CallbackContext) -> int:
    context.user_data['cpf'] = update.message.text
    await update.message.reply_text("Por fim, envie o tamanho da camisa (P, M, G, GG):")
    return CAMISA

# Função para capturar o tamanho da camisa e salvar no banco
async def get_camisa(update: Update, context: CallbackContext) -> int:
    context.user_data['camisa'] = update.message.text

    # Inserindo dados no banco
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO pessoas (nome, cpf, camisa) VALUES (%s, %s, %s)",
        (context.user_data['nome'], context.user_data['cpf'], context.user_data['camisa'])
    )
    db.commit()

    await update.message.reply_text("Informações salvas com sucesso!")
    return ConversationHandler.END

# Função para cancelar o processo
async def cancelar(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Operação cancelada.")
    return ConversationHandler.END

# Configurar os handlers
def main():
    app = ApplicationBuilder().token("8151041116:AAFUtV-cu0M8PdiJjFcO9C9YTbvUAyGztS0").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_nome)],
            CPF: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cpf)],
            CAMISA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_camisa)],
        },
        fallbacks=[CommandHandler('cancelar', cancelar)]
    )

    app.add_handler(conv_handler)

    print("Bot iniciado com sucesso!")
    app.run_polling()

if __name__ == '__main__':
    main()
