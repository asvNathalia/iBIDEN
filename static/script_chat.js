const chatToggle = document.getElementById('chatbot-toggle');
const chatContainer = document.getElementById('chat-container');
const closeBtn = document.getElementById('close-btn');
const options = document.getElementById('options');
const subOptions = document.getElementById('sub-options');
const userInput = document.getElementById('user-input');

// Inicia o chatbot fechado
chatContainer.style.display = 'none';


chatToggle.addEventListener('click', () => {
    if (chatContainer.style.display === 'block') {
        chatContainer.style.display = 'none';
    } else {
        chatContainer.style.display = 'block';
        options.style.display = 'block'; // Mostra opções ao abrir
        subOptions.style.display = 'none'; // Oculta sub-opções ao abrir
        userInput.value = ''; // Limpa campo de entrada
        mainOptions.style.display = 'block'; // Assegura que as opções principais estejam visíveis
    }
});



closeBtn.addEventListener('click', () => {
    chatContainer.style.display = 'none';
    options.style.display = 'none'; // Oculta opções ao fechar
    subOptions.style.display = 'none'; // Oculta sub-opções ao fechar
});


function showMainOptions() {
    options.style.display = 'block'; // Mostra as opções principais
    subOptions.style.display = 'none'; // Oculta as sub-opções
}

function showInitialMessage() {
    const initialMessage = `
        👋 Olá! Sou o ChatiBIDEN, pronto para te ajudar a entender mais sobre o clima e os casos de dengue! 
        Como posso te ajudar hoje? Escolha uma das opções abaixo ou digite <strong>Dengue</strong> para começar:
        <ul id="main-options">
            <li><a href="{{ url_for('busca_clima')}}">Ver dados climáticos 🌦️</a></li>
            <li><a href="{{ url_for('dengueinsight')}}">Visualizar Métricas da Dengue 🦟</a></li>
            <li><a href="{{ url_for('casosgrafico')}}">Previsão da Dengue 🚨</a></li>
            <li><a href="{{ url_for('buscar_impactos')}}">Saber mais sobre Impactos Ambientais 🔥</a></li>
            <li><a href="{{ url_for('mapadengue')}}">Mapa da Dengue no Brasil 🌎</a></li>
            <li><a href="{{ url_for('dashboard')}}">Acessar Dashboard 📈</a></li>
            <li><a class="option-btn" href="#" onclick="showSubOptions()">Explicação do Dashboard 👨‍🏫</a></li>
        </ul>
    `;
    
    addMessage('bot', initialMessage); // Adiciona a mensagem inicial ao chat
}

let currentContext = '';

function generateBotResponse(message) {
    const lowerMessage = message.toLowerCase();

    const includesKeywords = (keywords) => keywords.some(keyword => lowerMessage.includes(keyword));

    if (includesKeywords(['menu', 'voltar pro menu', 'voltar', 'menu principal', 'principal'])) {
        // Limpa o chat antes de mostrar as opções
        const chatBox = document.getElementById('chat-box');
        chatBox.innerHTML = ''; // Limpa todas as mensagens do chat
        currentContext = ''; // Reseta o contexto
        showInitialMessage(); // Adiciona a mensagem inicial
        showMainOptions(); // Exibe as opções principais
        return; // Termina a execução aqui
    }

    // Respostas com base no contexto atual
    if (currentContext === 'sintomas' && includesKeywords(['como se proteger', 'prevenção', 'proteger'])) {
        addMessage('bot', 'Para se proteger da dengue, é importante eliminar água parada, usar repelentes e evitar locais com alta incidência de mosquitos. Para saber mais digite <strong>medidas de controle</strong>');
        currentContext = 'proteção';
        return;
    } else if (currentContext === 'sintomas' && includesKeywords(['sintomas graves', 'graves'])) {
        addMessage('bot', 'Os sintomas graves da dengue incluem sangramentos, dor abdominal intensa e dificuldade para respirar. É importante procurar atendimento médico imediatamente. Posso ajudar com mais alguma informação?');
        currentContext = ''; // Finaliza o contexto após a resposta completa
        return;
    } else if (currentContext === 'proteção' && includesKeywords(['medidas de controle', 'controle', 'controle mosquito'])) {
        addMessage('bot', 'As medidas de controle incluem o uso de inseticidas e a limpeza de locais onde o mosquito possa se reproduzir. Para saber mais digite <strong>como colaborar</strong>');
        currentContext = 'controle';
        return;
    } else if (currentContext === 'controle') {
        if (includesKeywords(['sim'])) {
            addMessage('bot', 'Você pode colaborar informando a sua comunidade sobre a importância de eliminar água parada e reportando focos do mosquito. Alguma outra dúvida?');
            currentContext = 'dúvidas'; // Agora estamos no contexto de dúvidas
            return;
        } else if (includesKeywords(['não'])) {
            addMessage('bot', 'Obrigado pela conversa! 😊 Se precisar de mais informações, estarei por aqui! Caso queira voltar para o menu inicial, digite "menu"');
            currentContext = ''; // Finaliza o contexto
            return;
        }
    }

    // Respostas gerais (fora de um contexto específico)
    if (includesKeywords(['dengue', 'doença', 'mosquito'])) {
        addMessage('bot', 'A dengue é uma doença viral. Você gostaria de saber mais sobre <strong>sintomas</strong>, <strong>prevenção</strong>, <strong>vacinação</strong> ou <strong>transmissão</strong>?');
        currentContext = '';
    } else if (includesKeywords(['sintoma', 'sintomas'])) {
        addMessage('bot', 'Os sintomas da dengue incluem febre alta, dores de cabeça e dores no corpo. Você gostaria de saber <strong>como se proteger</strong> ou <strong>quais são os sintomas graves</strong>?');
        currentContext = 'sintomas';
    } else if (includesKeywords(['prevenção', 'prevenir'])) {
        addMessage('bot', 'A prevenção inclui eliminar água parada e usar repelentes. Tem interesse em saber mais sobre <strong>tratamento</strong>, <strong>vacinação</strong> ou <strong>medidas de controle</strong>?');
        currentContext = 'prevenção';
    } else if (includesKeywords(['vacinação', 'vacina'])) {
        addMessage('bot', 'A vacina contra a dengue é importante para prevenir a doença. Atualmente, existem várias vacinas disponíveis contra a dengue. A vacinação é recomendada para pessoas que vivem em áreas de risco. Se precisar de mais informações, estarei por aqui. Alguma outra dúvida?');
        currentContext = 'vacinação';
    } else if (includesKeywords(['tratamento', 'curar', 'cura'])) {
        addMessage('bot', 'O tratamento é geralmente sintomático, com hidratação e medicamentos. Posso ajudar com mais alguma coisa?');
        currentContext = ''; // Finaliza o contexto após a resposta completa
    } else if (includesKeywords(['transmissão', 'transmitir'])) {
        addMessage('bot', 'A dengue é transmitida principalmente pelo mosquito Aedes aegypti. Para saber mais, digite <strong>como evitar picadas</strong>');
        currentContext = 'transmissão';
    } else if (includesKeywords(['sintomas graves', 'grave', 'complicações'])) {
        addMessage('bot', 'Os sintomas graves da dengue incluem sangramentos, dor abdominal intensa e dificuldade para respirar. É importante procurar atendimento médico imediatamente. Posso ajudar com mais alguma informação?');
        currentContext = ''; // Finaliza o contexto após a resposta completa
    } else if (includesKeywords(['medidas de controle', 'medidas', 'medida','controle', 'controle mosquito', 'controle da dengue', 'controle dengue'])) {
        addMessage('bot', 'As medidas de controle incluem o uso de inseticidas e a limpeza de locais onde o mosquito possa se reproduzir. Para saber mais, digite <strong>como colaborar</strong>');
        currentContext = 'controle';
    } else if (includesKeywords(['como colaborar', 'ajudar', 'colaboração'])) {
        addMessage('bot', 'Você pode colaborar informando a sua comunidade sobre a importância de eliminar água parada e reportando focos do mosquito. Alguma outra dúvida?');
        currentContext = 'dúvidas';
    } else if (includesKeywords(['sim'])) {
        addMessage('bot', 'Você pode me perguntar sobre <strong>dengue</strong>, <strong>sintomas</strong>, <strong>prevenção</strong>, <strong>tratamento</strong>, <strong>controle da dengue</strong>, <strong>transmissão</strong>, ou <strong>vacinação</strong>.');
        currentContext = '';

    } else if (includesKeywords(['não', 'nao'])) {
        addMessage('bot', 'Obrigado pela conversa! Se precisar de mais informações, estarei por aqui. 😉! Para voltar ao menu principal, digite "menu"');
        currentContext = ''; // Finaliza o contexto
    }
    else {
        addMessage('bot', 'Desculpe, não entendi. Você pode me perguntar sobre <strong>dengue</strong>, <strong>sintomas</strong>, <strong>prevenção</strong>, <strong>tratamento</strong>, <strong>transmissão</strong> ou <strong>vacinação</strong>. Ou digite "menu" para voltar ao menu principal.');
        currentContext = ''; // Reseta o contexto em caso de erro
    }
}


function showSubOptions() {
    document.getElementById('sub-options').style.display = 'block'; // Mostrar as sub-opções
    document.getElementById('main-options').style.display = 'block'; // Garante que as opções principais estão visíveis
}


function goBack() {
    document.getElementById('sub-options').style.display = 'none';
    document.getElementById('main-options').style.display = 'block';
}

function explainTopic(topic) {
    let explanation;

    switch (topic) {
        case 'aumento-temperatura':
            explanation = `📈🌡️ A página mostra o aumento das temperaturas médias anuais no Brasil ao longo das décadas. De 1961-1990, a média era 22,33°C, subindo para 23,60°C entre 1990-2020. O gráfico também revela que todos os meses tiveram elevação de temperatura nesse período, indicando uma tendência de aquecimento contínuo, possivelmente causada pelas mudanças climáticas, o que pode influenciar a proliferação do Aedes aegypti.`;
            break;
        case 'dengue-e-clima':
            explanation = `A página mostra a correlação entre temperatura 🌡️ e casos de dengue 🦟 ao longo dos anos. No gráfico de linhas (parte superior), podemos ver que tanto a temperatura quanto os casos de dengue aumentam e diminuem em conjunto 📈. Picos de temperatura mais alta costumam coincidir com o aumento dos casos de dengue, sugerindo que o calor contribui para a proliferação do mosquito transmissor 🦠.
            <br><br>
            <strong>Destaque para 2020 (Ano da Pandemia 😷):</strong>
            Em 2020, houve uma queda significativa nos casos de dengue, enquanto a temperatura permaneceu estável. Isso pode ser resultado das medidas de distanciamento social e outras ações adotadas durante a pandemia de COVID-19 📉.`;
            break;
        case 'dengue-e-chuva':
            explanation = `🌧️ O impacto da chuva na proliferação da dengue é significativo, pois águas acumuladas após chuvas intensas servem como criadouros para o mosquito. 
            <br>O gráfico mostra que os casos de dengue 🦟 e a precipitação 🌧️ têm picos semelhantes ao longo dos anos e meses. Nos meses de maior chuva, como março e abril, há um aumento expressivo nos casos de dengue 📈. Já nos meses de menor precipitação, como agosto e setembro, os casos caem bastante 📉. Isso indica que a alta precipitação favorece a proliferação do mosquito 🦠.`;
            break;
        case 'como-se-proteger':
            explanation = `Para se proteger da dengue 🦟: elimine água parada 💧, use repelente 🧴, mantenha janelas fechadas 🚪, e descarte o lixo corretamente 🗑️. Com pequenas ações, podemos evitar grandes problemas!<br><br>
            E para saber mais sobre impactos da Dengue, explore todas as ferramentas iBIDEN! 🤗`;
            break;
        default:
            explanation = `Desculpe, não consegui encontrar informações sobre esse tópico.`;
    }

    // Adicionar a explicação ao chat
    if (explanation) {
        addMessage('bot', explanation); // Passa o autor e a mensagem correta
    }
    
    // Agora esconde as sub-opções depois que a mensagem foi adicionada
    document.getElementById('sub-options').style.display = 'none';
}





function addMessage(author, message) {
    const chatBox = document.getElementById('chat-box');
    const newMessage = document.createElement('div');

    // Adiciona a classe apropriada com base no autor
    newMessage.classList.add('message', author === 'user' ? 'user-message' : 'bot-message');

    // Verifica se a mensagem não está vazia
    if (message) {
        newMessage.innerHTML = message; // Adiciona o conteúdo da mensagem
    } else {
        newMessage.innerHTML = "Desculpe, não consegui entender a sua mensagem."; // Mensagem padrão para erro
    }

    // Adiciona a nova mensagem ao chat
    chatBox.appendChild(newMessage);
    chatBox.scrollTop = chatBox.scrollHeight; // Desce o scroll para o final
}

// Exemplo de como você pode chamar a função de explicação
function onSubOptionClick(topic) {
    explainTopic(topic); // Chama a função para explicar o tópico
}

function sendMessage() {
    const message = userInput.value.trim();
    if (message) {
        addMessage('user', message); // Adiciona a mensagem do usuário
        generateBotResponse(message); // Gera resposta do bot
        userInput.value = ''; // Limpa o campo de entrada após enviar
        options.style.display = 'none'; // Esconde as opções após enviar a mensagem
        subOptions.style.display = 'none'; // Esconde as sub-opções após enviar a mensagem
    }
}

function toggleExplanation() {
    const mainOptions = document.getElementById('main-options');
    const subOptions = document.getElementById('sub-options');

    mainOptions.classList.toggle('hidden'); // Esconde as opções principais
    subOptions.style.display = 'flex'; // Exibe as sub-opções
}


// Exemplo de interação do usuário
document.getElementById('sendButton').onclick = function() {
    const userMessage = document.getElementById('userInput').value;
    addMessage('user', userMessage);

    // Gerar resposta do bot
    generateBotResponse(userMessage);

    // Agora você pode chamar a função handleUserResponse, se apropriado
    if (userMessage.includes('sim') || userMessage.includes('não')) {
        handleUserResponse(userMessage);
    }
};

document.getElementById('sendButton').addEventListener('click', sendMessage);

// Permite enviar a mensagem pressionando "Enter"
userInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});
