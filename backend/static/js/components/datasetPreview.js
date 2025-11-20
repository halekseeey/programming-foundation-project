// Dataset Preview component
function groupColumns(headers) {
	// Group 1: NUTS code (if exists)
	const nutsCols = headers.filter(h => {
		const hLower = h.toLowerCase();
		return hLower.includes('nuts') || hLower === 'nuts_code';
	});
	
	// Group 2: Common columns (geo, TIME_PERIOD)
	const commonCols = headers.filter(h => {
		const hLower = h.toLowerCase();
		return hLower === 'geo' || hLower === 'time_period';
	});
	
	// Group 3: Columns from nrg_ind_ren (renewable share dataset)
	// These include: OBS_VALUE_nrg_ind_ren, LAST UPDATE_nrg_ind_ren, unit_nrg_ind_ren, freq, nrg_bal_category
	const renCols = headers.filter(h => {
		if (nutsCols.includes(h) || commonCols.includes(h)) return false;
		const hLower = h.toLowerCase();
		return hLower.includes('nrg_ind_ren') || 
		       hLower.includes('ind_ren') ||
		       (hLower === 'freq' && !hLower.includes('bal')) ||
		       hLower === 'nrg_bal_category';
	});
	
	// Group 4: Columns from nrg_bal (energy balance dataset)
	// These include: OBS_VALUE_nrg_bal, LAST UPDATE_nrg_bal, unit_nrg_bal, and any other bal columns
	const balCols = headers.filter(h => {
		if (nutsCols.includes(h) || commonCols.includes(h) || renCols.includes(h)) return false;
		const hLower = h.toLowerCase();
		return hLower.includes('nrg_bal') || 
		       (hLower.includes('_bal') && !hLower.includes('ind_ren') && !hLower.includes('category'));
	});
	
	// Group 5: Any remaining columns
	const otherCols = headers.filter(h => 
		!nutsCols.includes(h) && 
		!commonCols.includes(h) &&
		!renCols.includes(h) &&
		!balCols.includes(h)
	);
	
	// Return grouped columns in order
	return {
		nuts: nutsCols,
		common: commonCols,
		ren: renCols,
		bal: balCols,
		other: otherCols,
		all: [...nutsCols, ...commonCols, ...renCols, ...balCols, ...otherCols]
	};
}

async function loadDatasetPreview() {
	try {
		const data = await API.datasetPreview('merged_dataset', 50);

		if (data.preview && data.preview.length > 0) {
			const allHeaders = Object.keys(data.preview[0]);
			const grouped = groupColumns(allHeaders);
			const headers = grouped.all;
			
			// Create single header row with grouped columns and visual separators
			const groups = [
				{ name: 'NUTS Code', cols: grouped.nuts },
				{ name: 'Common', cols: grouped.common },
				{ name: 'Renewable Share (nrg_ind_ren)', cols: grouped.ren },
				{ name: 'Energy Balance (nrg_bal)', cols: grouped.bal },
				{ name: 'Other', cols: grouped.other }
			];
			
			// Create map of column index to group for easier lookup
			const colToGroup = {};
			groups.forEach((group, groupIdx) => {
				group.cols.forEach((h) => {
					const colIdx = headers.indexOf(h);
					if (colIdx >= 0) {
						colToGroup[colIdx] = { groupIdx, isFirst: group.cols.indexOf(h) === 0 };
					}
				});
			});
			
			let headerRows = '<tr>';
			headers.forEach((h, idx) => {
				headerRows += `<th class="px-3 py-2 text-left border border-slate-700 font-semibold bg-slate-800">${h}</th>`;
			});
			headerRows += '</tr>';
			
			let tableHtml = `
                <div class="bg-slate-800/60 rounded-lg overflow-auto">
                    <table class="w-full text-xs border-collapse">
                        <thead class="sticky top-0 bg-slate-800 z-10">
                            ${headerRows}
                        </thead>
                        <tbody>
                            ${data.preview
								.map(
									(row) => `
                                <tr class="hover:bg-slate-800/40 transition-colors">
                                    ${headers.map((h) => `<td class="px-3 py-2 border border-slate-700">${row[h] ?? ''}</td>`).join('')}
                                </tr>
                            `
								)
								.join('')}
                        </tbody>
                    </table>
                </div>
                <div class="mt-3 text-xs text-slate-400">
                    <p>Showing ${data.preview.length} of ${data.total_rows} rows</p>
                </div>
            `;
			document.getElementById('dataset-preview-container').innerHTML = tableHtml;
		} else {
			document.getElementById('dataset-preview-container').innerHTML = `
                <div class="text-center py-8 text-slate-400">
                    <p>No preview data available</p>
                </div>
            `;
		}
	} catch (error) {
		console.error('Failed to load dataset preview:', error);
		document.getElementById('dataset-preview-container').innerHTML = `
            <div class="text-center py-8 text-red-400">
                <p>Error loading preview: ${error.message}</p>
            </div>
        `;
	}
}

// Setup modal handlers
function setupDatasetPreviewModal() {
	const loadBtn = document.getElementById('load-preview-btn');
	const modal = document.getElementById('dataset-preview-modal');
	const closeBtn = document.getElementById('close-preview-modal-btn');

	if (loadBtn && modal && closeBtn) {
		loadBtn.addEventListener('click', async () => {
			modal.style.display = 'flex';
			document.getElementById('dataset-preview-container').innerHTML = `
                <div class="text-center py-8">
                    <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-sky-500"></div>
                    <p class="text-sm text-slate-400 mt-2">Loading preview...</p>
                </div>
            `;
			await loadDatasetPreview();
		});

		closeBtn.addEventListener('click', () => {
			modal.style.display = 'none';
		});

		modal.addEventListener('click', (e) => {
			if (e.target === modal) {
				modal.style.display = 'none';
			}
		});

		// Close on Escape key
		document.addEventListener('keydown', (e) => {
			if (e.key === 'Escape' && modal.style.display === 'flex') {
				modal.style.display = 'none';
			}
		});
	}
}
