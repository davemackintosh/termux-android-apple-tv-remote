<script lang="ts">
	import {onMount} from "svelte"
	import { page } from '$app/stores';
	let pin: string = '';

	$: deviceId = $page.params.id;
	$: if (deviceId) initiatePair() 

	async function initiatePair() {
		fetch('http://localhost:8080/pair/' + deviceId)
			.then((res) => res.json())
			.then(console.log)
			.catch(console.error)
	}

	onMount(initiatePair)

	async function handlePin() {
		fetch(`http://localhost:8080/pair/${deviceId}/${pin}`)
			.then((res) => res.json())
			.then(console.log)
			.catch(console.error)
	}
	
</script>

<div>
<form on:submit|preventDefault={handlePin}>
	<label for="pin">Enter the pin on your Apple TV</label>
	<input type="text" bind:value={pin} />
	<button type="submit">pair</button>
</form>
</div>
