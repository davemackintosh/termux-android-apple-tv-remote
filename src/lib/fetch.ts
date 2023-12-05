import type { Writable } from 'svelte/store';
import { writable } from 'svelte/store';

interface returnType<T> {
	loading: Writable<boolean>;
	data: Writable<T | null>;
	error: Writable<Error | null>;
	refetch: (options?: RequestOptions) => void;
	promise?: Promise<T>;
}

export interface RequestOptions {
	fetchNow?: boolean;
	variables?: Record<string, unknown>;
}

export function apiRequest<T>(url: string, options: RequestOptions = {}): returnType<T> {
	const data = writable<T | null>();
	const error = writable<Error | null>();
	const loading = writable(!!options?.fetchNow);
	let body: string | undefined;

	function refetch(options: RequestOptions = {}): returnType<T> {
		loading.set(true);
		const method = options.variables ? 'POST' : 'GET';
		const headers = {
			'Content-Type': 'application/json'
		};

		if (options.variables) {
			body = JSON.stringify(options.variables);
		}
		const promise = fetch('http://localhost:8080' + url, {
			method,
			body,
			headers
		})
			.then((res) => res.json())
			.then((res: T) => {
				loading.set(false);
				data.set(res);
				error.set(null);
			});

		promise.catch((err) => {
			loading.set(false);
			error.set(err);
			data.set(null);
		});

		return {
			data,
			error,
			loading,
			refetch,
			promise: promise as Promise<T>
		};
	}

	if (typeof options.fetchNow === 'undefined' || options.fetchNow === true) {
		return refetch(options);
	} else {
		return {
			data,
			error,
			loading,
			refetch
		};
	}
}
