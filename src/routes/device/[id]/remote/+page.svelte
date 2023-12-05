<script lang="ts">
	import { page } from '$app/stores';
	import { apiRequest } from '$lib/fetch';

	const { loading: connecting } = apiRequest(`/devices/${$page.params.id}/connect`);
	const { refetch: sendCommand } = apiRequest(`/devices/${$page.params.id}/remote_control`, {
		fetchNow: false
	});

	enum Command {
		UP = 'up',
		RIGHT = 'right',
		DOWN = 'down',
		LEFT = 'left',
		MENU = 'menu',
		SELECT = 'select',
		PLAY = 'play',
		PAUSE = 'pause',
		HOME = 'home'
	}

	function up() {
		sendCommand({
			variables: {
				command: Command.UP
			}
		});
	}
	function right() {
		sendCommand({
			variables: {
				command: Command.RIGHT
			}
		});
	}
	function down() {
		sendCommand({
			variables: {
				command: Command.DOWN
			}
		});
	}
	function left() {
		sendCommand({
			variables: {
				command: Command.LEFT
			}
		});
	}
	function menu() {
		sendCommand({
			variables: {
				command: Command.MENU
			}
		});
	}
	function select() {
		sendCommand({
			variables: {
				command: Command.SELECT
			}
		});
	}
	function play() {
		sendCommand({
			variables: {
				command: Command.PLAY
			}
		});
	}
	function pause() {
		sendCommand({
			variables: {
				command: Command.PAUSE
			}
		});
	}
	function home() {
		sendCommand({
			variables: {
				command: Command.HOME
			}
		});
	}
</script>

<div class="remote">
	<button disabled={$connecting} class="up" on:click|preventDefault={up}>up</button>
	<button disabled={$connecting} class="right" on:click|preventDefault={right}>right</button>
	<button disabled={$connecting} class="down" on:click|preventDefault={down}>down</button>
	<button disabled={$connecting} class="left" on:click|preventDefault={left}>left</button>
	<button disabled={$connecting} class="home" on:click|preventDefault={home}>home</button>
	<button disabled={$connecting} class="play" on:click|preventDefault={play}>play</button>
	<button disabled={$connecting} class="pause" on:click|preventDefault={pause}>pause</button>
	<button disabled={$connecting} class="menu" on:click|preventDefault={menu}>menu</button>
	<button disabled={$connecting} class="select" on:click|preventDefault={select}>select</button>
</div>
