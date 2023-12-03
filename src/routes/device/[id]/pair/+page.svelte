<script lang="ts">
	import { page } from '$app/stores';
	let pin: string = '';

	$: deviceId = $page.params.id;

	$: fetch(`http://localhost:8080/connect/${deviceId}`)
		.then((res) => res.json())
		.then(() =>
			fetch('http://localhost:8080/pair/' + deviceId)
				.then((res) => res.json())
				.then(console.log)
		);
</script>

<div>
	<label for="pin">Enter the pin on your Apple TV</label>
	<input type="text" bind:value={pin} />
</div>
