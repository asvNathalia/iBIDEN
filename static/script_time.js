const mainElement = document.querySelector('.conteudo-principal');

const horaAtual = new Date().getHours();

if (horaAtual >= 6 && horaAtual < 18) {
    mainElement.classList.add('main-dia');
} else {
    mainElement.classList.add('main-noite');
}
