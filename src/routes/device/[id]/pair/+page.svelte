<script lang="ts">
	import { page } from '$app/stores';
	import { apiRequest } from '$lib/fetch';
	import type { DeviceDetails } from '$lib/types';

	interface Step {
		index: number;
		protocol: string;
		complete: boolean;
	}

	interface PairingPinResponse {
		status: string;
		protocol: string;
	}

	let requiredSteps: Step[] = [];

	let pin = '';
	let protocol: string = '';
	let currentStep = 0;
	const {
		error: deviceError,
		loading: deviceLoading,
		data: device
	} = apiRequest<DeviceDetails>(`/devices/${$page.params.id}`);
	const {
		error: pairError,
		loading: pairLoading,
		refetch: initiatePairing
	} = apiRequest(`/devices/${$page.params.id}/pair`, {
		fetchNow: false
	});
	const {
		error: pinError,
		data: pinData,
		loading: pinLoading,
		refetch: sendPin
	} = apiRequest<PairingPinResponse>(`/devices/${$page.params.id}/pair/pin`, {
		fetchNow: false
	});

	async function handlePin(protocol: string, pin: string) {
		sendPin({
			variables: {
				protocol,
				pin
			}
		}).promise.then(() => {
			pin = '';
			startPairingProcess();
		});
	}

	function startPairingProcess() {
		currentStep += 1;

		if ($device)
			initiatePairing({
				variables: {
					protocol: $device.services[currentStep - 1].name
				}
			});
	}

	$: requiredSteps =
		$device?.services.map(
			(service, index): Step => ({
				index,
				protocol: service.name,
				complete: false
			})
		) ?? [];
	$: requiredSteps = requiredSteps.map((step) => ({
		...step,
		complete: step.protocol === $pinData?.protocol
	}));
</script>

<div>
	{#if $deviceError}
		<div class="error">Couldn't get device info {$deviceError?.message}</div>
	{/if}
	{#if $pairError}
		<div class="error">Failed to initiate pairing {$pairError?.message}</div>
	{/if}
	{#if $pinError}
		<div class="error">Failed to send pin {$pinError?.message}</div>
	{/if}
	{#if $device}
		{#if !currentStep}
			<p>
				You will need to pair {requiredSteps.length} times to get remote functionality) I have no idea
				why...
			</p>
			<button on:click={startPairingProcess}>Get started</button>
		{:else}
			{@const pairingStep = requiredSteps[currentStep - 1]}
			<form on:submit|preventDefault={() => handlePin(pairingStep.protocol, pin)}>
				<h2>Step #{pairingStep.index + 1}</h2>
				<label for="pin">Enter the pin on your Apple TV to pair ({pairingStep.protocol})</label>
				<input type="text" bind:value={pin} disabled={$pairLoading || $deviceLoading} />
				<input type="hidden" bind:value={protocol} value={pairingStep.protocol} />

				<button type="submit" disabled={$pinLoading || $deviceLoading}>pair</button>
			</form>
		{/if}
	{:else}
		<p>loading device information</p>
	{/if}
</div>
