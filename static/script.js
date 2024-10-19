/*MAPA DE CALOR*/

function toggleTooltip(element) {
    element.classList.toggle('active');
}

const options = {
    key: 'XBRUBIYWAgEfw9jep7gk7p7vshfRtZ8m', // SUBSTITUA PELA SUA PRÓPRIA CHAVE !!!

    // Mantenha as outras configurações iniciais
    zoom: 5,
    timestamp: Date.now() + 3 * 24 * 60 * 60 * 1000,
    hourFormat: '12h',
    // ...etc
};


windyInit(options, windyAPI => {
    const { map, picker, utils, broadcast, storer  } = windyAPI;
    const locationInput = document.getElementById('locationInput');

    // Função para atualizar o mapa com base na localização
    function updateMapWithLocation(latitude, longitude) {
        map.setView([latitude, longitude], map.getZoom());
    }

    // Função para obter coordenadas com base na pesquisa de localização
    function getCoordinatesFromLocation(location) {
        // Use uma API de geocodificação, como a do OpenStreetMap
        // Substitua a URL pela URL da API de geocodificação que você deseja usar
        const geocodingUrl = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(location)}`;

        fetch(geocodingUrl)
            .then(response => response.json())
            .then(data => {
                if (data && data.length > 0) {
                    const { lat, lon } = data[0];
                    updateMapWithLocation(lat, lon);
                } else {
                    console.error('Localização não encontrada.');
                }
            })
            .catch(error => {
                console.error('Erro ao obter coordenadas:', error);
            });
    }
    
    // Botão de pesquisa
    const searchButton = document.getElementById('searchButton');
    searchButton.addEventListener('click', () => {
        const location = locationInput.value;
        if (location) {
            getCoordinatesFromLocation(location);
        } else {
            console.error('Por favor, insira um local válido.');
        }
    });
});