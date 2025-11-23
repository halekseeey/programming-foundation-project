// Regions Ranking component
function renderRegionsRanking(data) {
	if (!data || data.error) {
		document.getElementById('regions-ranking-container').innerHTML = `
            <section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
                <h2 class="text-lg font-semibold mb-4">Regions Ranking</h2>
                <p class="text-sm text-slate-400">${data?.error || 'No data available'}</p>
            </section>
        `;
		return;
	}

	document.getElementById('regions-ranking-container').innerHTML = `
        <section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-6">
            <div class="flex items-center justify-between">
                <h2 class="text-lg font-semibold">Regions Ranking</h2>
                ${data.metric_used ? `<span class="text-xs text-slate-400">(${data.metric_used})</span>` : ''}
            </div>
            <p class="text-xs text-slate-400">💡 Regions are ranked by current renewable energy adoption and growth rates.</p>

            ${
				data.leading_by_value && data.leading_by_value.length > 0
					? `
                <div>
                    <h3 class="text-sm font-semibold mb-3">Leading by Current Value</h3>
                    <p class="text-xs text-slate-500 mb-2">
                        <strong>Growth rate:</strong> Average annual increase in percentage points per year (linear regression slope). 
                        <strong>Change:</strong> Total percentage change from first to last available value. 
                        <strong>Data points:</strong> Number of years with available data.
                    </p>
                    <div class="h-[300px] overflow-y-auto space-y-2">
                        ${data.leading_by_value
							.map(
								(region, idx) => `
                            <div class="bg-slate-800/60 rounded-lg p-3 w-full">
                                <div class="flex items-center justify-between">
                                    <div class="flex items-center gap-3">
                                        <span class="text-xs text-slate-400 w-6">#${idx + 1}</span>
                                        <span class="text-sm font-semibold">${region.region}</span>
                                    </div>
                                    <div class="flex items-center gap-4 text-xs">
                                        <div class="flex items-center gap-2">
                                            <span class="text-slate-400">Growth rate:</span>
                                            <span class="font-semibold ${
												region.growth_rate >= 0 ? 'text-green-400' : 'text-red-400'
											}">
                                                ${region.growth_rate >= 0 ? '+' : ''}${region.growth_rate.toFixed(3)}
                                            </span>
                                        </div>
                                        <div class="flex items-center gap-2">
                                            <span class="text-slate-400">Change:</span>
                                            <span class="font-semibold ${
												region.total_change_pct >= 0 ? 'text-green-400' : 'text-red-400'
											}">
                                                ${region.total_change_pct >= 0 ? '+' : ''}${region.total_change_pct.toFixed(2)}%
                                            </span>
                                        </div>
                                        <div class="flex items-center gap-2">
                                            <span class="text-slate-400">Data points:</span>
                                            <span class="font-semibold">${region.data_points}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `
							)
							.join('')}
                    </div>
                </div>
            `
					: ''
			}

            ${
				data.fastest_growing && data.fastest_growing.length > 0
					? `
                <div>
                    <h3 class="text-sm font-semibold mb-3">Fastest Growing</h3>
                    <p class="text-xs text-slate-500 mb-2">
                        <strong>Growth rate:</strong> Average annual increase in percentage points per year (linear regression slope). 
                        <strong>Last available:</strong> Last available value (latest year in dataset). 
                        <strong>Change:</strong> Total percentage change from first to last available value.
                    </p>
                    <div class="h-[300px] overflow-y-auto space-y-2">
                        ${data.fastest_growing
							.map(
								(region, idx) => `
                            <div class="bg-slate-800/60 rounded-lg p-3 w-full">
                                <div class="flex items-center justify-between">
                                    <div class="flex items-center gap-3">
                                        <span class="text-xs text-slate-400 w-6">#${idx + 1}</span>
                                        <span class="text-sm font-semibold">${region.region}</span>
                                    </div>
                                    <div class="flex items-center gap-4 text-xs">
                                        <div class="flex items-center gap-2">
                                            <span class="text-slate-400">Growth rate:</span>
                                            <span class="font-semibold ${
												region.growth_rate >= 0 ? 'text-green-400' : 'text-red-400'
											}">
                                                ${region.growth_rate >= 0 ? '+' : ''}${region.growth_rate.toFixed(3)}
                                            </span>
                                        </div>
                                        <div class="flex items-center gap-2">
                                            <span class="text-slate-400">Last available:</span>
                                            <span class="font-semibold">${region.last_value.toFixed(2)}</span>
                                        </div>
                                        <div class="flex items-center gap-2">
                                            <span class="text-slate-400">Change:</span>
                                            <span class="font-semibold ${
												region.total_change_pct >= 0 ? 'text-green-400' : 'text-red-400'
											}">
                                                ${region.total_change_pct >= 0 ? '+' : ''}${region.total_change_pct.toFixed(2)}%
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `
							)
							.join('')}
                    </div>
                </div>
            `
					: ''
			}

            ${
				data.lagging && data.lagging.length > 0
					? `
                <div>
                    <h3 class="text-sm font-semibold mb-3">Lagging Regions</h3>
                    <p class="text-xs text-slate-500 mb-2">
                        <strong>Growth rate:</strong> Average annual increase in percentage points per year (linear regression slope). 
                        <strong>Change:</strong> Total percentage change from first to last available value. 
                        <strong>Data points:</strong> Number of years with available data.
                    </p>
                    <div class="h-[300px] overflow-y-auto space-y-2">
                        ${data.lagging
							.map(
								(region, idx) => `
                            <div class="bg-slate-800/60 rounded-lg p-3 w-full">
                                <div class="flex items-center justify-between">
                                    <div class="flex items-center gap-3">
                                        <span class="text-xs text-slate-400 w-6">#${idx + 1}</span>
                                        <span class="text-sm font-semibold">${region.region}</span>
                                    </div>
                                    <div class="flex items-center gap-4 text-xs">
                                        <div class="flex items-center gap-2">
                                            <span class="text-slate-400">Growth rate:</span>
                                            <span class="font-semibold ${
												region.growth_rate >= 0 ? 'text-green-400' : 'text-red-400'
											}">
                                                ${region.growth_rate >= 0 ? '+' : ''}${region.growth_rate.toFixed(3)}
                                            </span>
                                        </div>
                                        <div class="flex items-center gap-2">
                                            <span class="text-slate-400">Change:</span>
                                            <span class="font-semibold ${
												region.total_change_pct >= 0 ? 'text-green-400' : 'text-red-400'
											}">
                                                ${region.total_change_pct >= 0 ? '+' : ''}${region.total_change_pct.toFixed(2)}%
                                            </span>
                                        </div>
                                        <div class="flex items-center gap-2">
                                            <span class="text-slate-400">Data points:</span>
                                            <span class="font-semibold">${region.data_points}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `
							)
							.join('')}
                    </div>
                </div>
            `
					: ''
			}
        </section>
    `;
}
