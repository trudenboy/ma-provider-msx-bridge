// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://trudenboy.github.io/ma-provider-msx-bridge',
	base: '/ma-provider-msx-bridge',
	integrations: [
		starlight({
			title: 'MSX Bridge · MA Provider',
			editLink: {
				baseUrl: 'https://github.com/trudenboy/ma-provider-msx-bridge/edit/feat/msx-bridge-player-provider/docs-site/src/content/docs/',
			},
			social: [
				{ icon: 'github', label: 'GitHub', href: 'https://github.com/trudenboy/ma-provider-msx-bridge' },
			],
			sidebar: [
				{ label: 'Home', slug: 'index' },
				{ label: 'Configuration', slug: 'configuration' },
				{ label: 'Features', autogenerate: { directory: 'features' } },
				{ label: 'Development', items: [
					{ label: 'Dev Environment', slug: 'development' },
					{ label: 'Docker', slug: 'dev-docker' },
					{ label: 'Testing', slug: 'testing' },
					{ label: 'Contributing', slug: 'contributing' },
					{ label: 'Incident Management', slug: 'incident-management' },
				] },
			],
		}),
	],
});
