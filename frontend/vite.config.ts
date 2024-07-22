import react from '@vitejs/plugin-react-swc';
import { defineConfig } from 'vite';

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [react()],
	build: {
		emptyOutDir: true,
	},
	server: {
		host: '0.0.0.0',
		port: 3000,
	},
});
