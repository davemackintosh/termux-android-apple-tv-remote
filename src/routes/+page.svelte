<script context="module" lang="ts">
</script>

<script lang="ts">
	import { goto } from '$app/navigation';
	import { apiRequest } from '$lib/fetch';
	import type { DeviceDetails } from '$lib/types';

	const { data, loading, error, refetch } = apiRequest<DeviceDetails[]>('/devices', {
		fetchNow: false
	});

	let storedDevices: DeviceDetails[] = [];
	if (typeof window !== 'undefined') {
		storedDevices = JSON.parse(localStorage.getItem('discoveredDevices') ?? '[]');
	}

	function initiateScan() {
		refetch();
	}
	function initiatePair(device: DeviceDetails) {
		goto(`/device/${device.identifier}/pair/`);
	}

	$: availableDevices = $data?.length ? $data : storedDevices;
	$: typeof window !== 'undefined'
		? localStorage.setItem('discoveredDevices', JSON.stringify(availableDevices))
		: null;
</script>

<div class="main-menu">
	{#if $error}
		<div class="error">{$error?.message}</div>
	{/if}
	{#each availableDevices as device}
		<div class="device-row">
			<div class="device-info">
				<p><a href="/device/{device.identifier}/remote"><strong>{device.name}</strong></a></p>
				<div class="services">
					{#each device.services as service}
						<p><em>{service.name}</em></p>
					{/each}
				</div>
			</div>
			<div class="device-actions">
				<button on:click={() => initiatePair(device)}>Pair/Connect</button>
			</div>
		</div>
	{/each}
	<button on:click={initiateScan} disabled={$loading}>Scan for devices</button>
</div>

<style>
	p {
		margin-bottom: 0;
	}
	.error {
		background-color: pink;
		color: red;
		border: 1px solid red;
	}

	.device-row {
		display: flex;
		flex-direction: row;
		margin-bottom: 1em;
	}

	.device-row .services {
		display: flex;
		flex-direction: row;
		gap: 1em;
	}

	.device-info {
		flex-grow: 1;
	}
	.device-actions {
		flex-shrink: 1;
	}
</style>
