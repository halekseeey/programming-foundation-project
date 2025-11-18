'use client';

import { useEffect, useState } from 'react';

interface PreviewData {
	dataset_id: string;
	total_rows: number;
	total_columns: number;
	columns: string[];
	preview: Array<Record<string, unknown>>;
	dtypes: Record<string, string>;
}

interface Props {
	datasetId: string | null;
}

export function DatasetPreview({ datasetId }: Props) {
	const [preview, setPreview] = useState<PreviewData | null>(null);
	const [loading, setLoading] = useState(false);
	const [isOpen, setIsOpen] = useState(false);
	const [isFullDataset, setIsFullDataset] = useState(false);

	const fetchPreview = async (numRows: number) => {
		if (!datasetId) return;

		setLoading(true);
		try {
			const res = await fetch(
				`${
					process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000'
				}/api/datasets/preview?dataset_id=${datasetId}&rows=${numRows}`
			);
			const data = await res.json();
			setPreview(data);
			setIsFullDataset(data.preview.length >= data.total_rows);
		} catch (error) {
			console.error('Failed to fetch preview:', error);
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		if (isOpen && datasetId) {
			fetchPreview(10);
		}
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [isOpen, datasetId]);

	const handleLoadFull = () => {
		if (preview) {
			fetchPreview(preview.total_rows);
		}
	};

	if (!datasetId) return null;

	return (
		<>
			<button
				onClick={() => setIsOpen(true)}
				className="text-xs px-3 py-2 rounded-xl border border-slate-700 hover:border-sky-500 hover:text-sky-300 transition"
			>
				Preview Dataset
			</button>

			{isOpen && (
				<div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
					<div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 max-w-6xl w-full max-h-[90vh] overflow-y-auto">
						<div className="flex items-center justify-between mb-6">
							<div>
								<h2 className="text-2xl font-bold">Dataset Preview</h2>
								<p className="text-sm text-slate-400 mt-1">{datasetId}</p>
							</div>
							<button onClick={() => setIsOpen(false)} className="text-slate-400 hover:text-white transition">
								<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
								</svg>
							</button>
						</div>

						{loading ? (
							<div className="text-center py-8 text-slate-400">Loading preview...</div>
						) : preview ? (
							<div className="space-y-4">
								<div className="flex items-center justify-between text-sm">
									<div className="flex items-center gap-4">
										<span className="text-slate-400">
											Showing <strong className="text-white">{preview.preview.length}</strong> of{' '}
											<strong className="text-white">{preview.total_rows}</strong> rows
										</span>
										<span className="text-slate-400">
											<strong className="text-white">{preview.total_columns}</strong> columns
										</span>
									</div>
									{!isFullDataset && (
										<button
											onClick={handleLoadFull}
											disabled={loading}
											className="px-4 py-2 bg-sky-600 hover:bg-sky-700 rounded-lg text-sm transition disabled:opacity-50"
										>
											{loading ? 'Loading...' : 'Load Full Dataset'}
										</button>
									)}
								</div>

								<div className="max-h-[400px] overflow-y-auto overflow-x-auto border border-slate-700 rounded-lg">
									<table className="w-full text-sm">
										<thead className="sticky top-0 bg-slate-800 z-10">
											<tr className="border-b border-slate-700">
												{preview.columns.map((col) => (
													<th key={col} className="text-left py-2 px-3 font-semibold">
														<div className="flex flex-col">
															<span>{col}</span>
															<span className="text-xs font-normal text-slate-400">
																{preview.dtypes[col]}
															</span>
														</div>
													</th>
												))}
											</tr>
										</thead>
										<tbody>
											{preview.preview.map((row, idx) => (
												<tr key={idx} className="border-b border-slate-800/50 hover:bg-slate-800/30">
													{preview.columns.map((col) => (
														<td key={col} className="py-2 px-3">
															<span className="font-mono text-xs">{String(row[col] ?? '')}</span>
														</td>
													))}
												</tr>
											))}
										</tbody>
									</table>
								</div>
							</div>
						) : (
							<div className="text-center py-8 text-slate-400">No preview available</div>
						)}
					</div>
				</div>
			)}
		</>
	);
}
