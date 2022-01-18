var map = L.map('map').setView([50.47616, 30.3352], 17);

L.tileLayer( 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    subdomains: ['a','b','c']
}).addTo( map );


var imageUrl = 'img.png',
    imageBounds = [[50.47789, 30.33266], [50.47443, 30.33774]];
L.imageOverlay(imageUrl, imageBounds).setOpacity(0.5).addTo(map);

const pinOptions = {draggable: true, title: 'pin'};
L.marker(imageBounds[0], pinOptions).addTo(map);
L.marker([imageBounds[0][0], imageBounds[1][1]], pinOptions).addTo(map);
L.marker(imageBounds[1], pinOptions).addTo(map);
L.marker([imageBounds[1][0], imageBounds[0][1]], pinOptions).addTo(map);
