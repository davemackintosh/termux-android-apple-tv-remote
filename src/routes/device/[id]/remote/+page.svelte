<script lang="ts">
	import { page } from '$app/stores';
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

	$: deviceId = $page.params.id;

	async function sendCommand(command: Command) {
		await fetch(`http://localhost:8080/connect/${deviceId}`);
		fetch(`http://localhost:8080/remote_control/${deviceId}/${command}`)
			.then((res) => res.json())
			.then(console.log);
	}
	function up() {
		sendCommand(Command.UP);
	}
	function right() {
		sendCommand(Command.RIGHT);
	}
	function down() {
		sendCommand(Command.DOWN);
	}
	function left() {
		sendCommand(Command.LEFT);
	}
	function menu() {
		sendCommand(Command.MENU);
	}
	function select() {
		sendCommand(Command.SELECT);
	}
	function play() {
		sendCommand(Command.PLAY);
	}
	function pause() {
		sendCommand(Command.PAUSE);
	}
	function home() {
		sendCommand(Command.HOME);
	}
</script>

<div class="remote">
	<button class="up" on:click|preventDefault={up}>up</button>
	<button class="right" on:click|preventDefault={right}>right</button>
	<button class="down" on:click|preventDefault={down}>down</button>
	<button class="left" on:click|preventDefault={left}>left</button>
	<button class="home" on:click|preventDefault={home}>home</button>
	<button class="play" on:click|preventDefault={play}>play</button>
	<button class="pause" on:click|preventDefault={pause}>pause</button>
	<button class="menu" on:click|preventDefault={menu}>menu</button>
	<button class="select" on:click|preventDefault={select}>select</button>
</div>
