import { io } from 'socket.io-client';

const socket = io(import.meta.env.PROD ? '/' : 'http://localhost:5000', {
    autoConnect: true,
    transports: ['websocket']
});

export default socket;
