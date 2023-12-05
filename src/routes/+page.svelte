<script context="module" lang="ts">
	export interface DeviceDetails {
		name: string;
		identifier: string;
	}
</script>

<script lang="ts">
	import { goto } from '$app/navigation';

	let storedDevices: DeviceDetails[] = [];
	if (typeof window !== 'undefined') {
		storedDevices = JSON.parse(localStorage.getItem('discoveredDevices') ?? '[]');
	}

	let devices: DeviceDetails[] = storedDevices;

	function initiateScan() {
		fetch('http://localhost:8080/devices.json')
			.then((res) => res.json())
			.then((discoveredDevices) => {
				devices = discoveredDevices;

				if (typeof window !== 'undefined') {
					localStorage.setItem('discoveredDevices', JSON.stringify(discoveredDevices));
				}
			});
	}
	function initiatePair(device: DeviceDetails) {
		goto(`/device/${device.identifier}/pair/`);
	}

	$: availableDevices = devices.length ? devices : [];
	console.log(availableDevices)
</script>

<div class="main-menu">
	{#each availableDevices as device}
		<div class="device-row">
			<p><a href="/device/{device.identifier}/remote"><strong>{device.name}</strong></a></p>
			{#each device.services as service}
				<p><em>{service.name}</em></p>
			{/each}
			<button on:click={() => initiatePair(device)}>Pair/Connect</button>
		</div>
	{/each}
	<button on:click={initiateScan}>Scan for devices</button>
</div>
