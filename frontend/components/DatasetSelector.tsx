'use client';

import { useEffect, useState } from 'react';
import * as Dialog from '@radix-ui/react-dialog';

export interface Dataset {
	id: string;
	name: string;
	filename: string;
	path: string;
}

interface PreviewData {
	dataset_id: string;
	total_rows: number;
	total_columns: number;
	columns: string[];
	preview: Array<Record<string, unknown>>;
	dtypes: Record<string, string>;
}

interface Props {
	onSelect: (datasets: Dataset[]) => void;
}

export function DatasetSelector({ onSelect }: Props) {
	const [datasets, setDatasets] = useState<Dataset[]>([]);
	const [selectedDatasets, setSelectedDatasets] = useState<Set<string>>(new Set());
	const [preview, setPreview] = useState<PreviewData | null>(null);
	const [previewDataset, setPreviewDataset] = useState<Dataset | null>(null);
	const [previewLoading, setPreviewLoading] = useState(false);
	const [showPreview, setShowPreview] = useState(false);

	useEffect(() => {
		fetchDatasets();
	}, []);

	const fetchDatasets = async () => {
		try {
			const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000'}/api/datasets`);
			const data = await res.json();
			setDatasets(data.datasets || []);
		} catch (error) {
			console.error('Failed to fetch datasets:', error);
		}
	};

	const fetchPreview = async (dataset: Dataset, loadFull: boolean = false) => {
		setPreviewLoading(true);
		setPreviewDataset(dataset);
		try {
			const rows = loadFull ? 999999 : 10;
			const res = await fetch(
				`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000'}/api/datasets/preview?dataset_id=${
					dataset.id
				}&rows=${rows}`
			);
			const data = await res.json();
			setPreview(data);
			setShowPreview(true); // Open modal after data is loaded
		} catch (error) {
			console.error('Failed to fetch preview:', error);
		} finally {
			setPreviewLoading(false);
		}
	};

	const handleToggleDataset = (dataset: Dataset) => {
		setSelectedDatasets((prev) => {
			const newSet = new Set(prev);
			if (newSet.has(dataset.id)) {
				newSet.delete(dataset.id);
			} else {
				newSet.add(dataset.id);
			}
			return newSet;
		});
	};

	const handleSelect = () => {
		if (selectedDatasets.size >= 2) {
			const selected = datasets.filter((d) => selectedDatasets.has(d.id));
			onSelect(selected);
		}
	};

	return (
		<div className="space-y-8 pb-24">
			<div className="text-center space-y-3">
				<h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-sky-400 to-blue-500 bg-clip-text text-transparent">
					Select Datasets
				</h1>
				<p className="text-sm text-slate-400">Select exactly 2 datasets to merge and analyze</p>
			</div>

			<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				{datasets.map((dataset) => {
					const isSelected = selectedDatasets.has(dataset.id);
					return (
						<div
							key={dataset.id}
							className={`group relative rounded-2xl border-2 transition-all overflow-hidden flex flex-col ${
								isSelected
									? 'border-sky-500 bg-slate-900/60 shadow-lg shadow-sky-500/20'
									: 'border-slate-700 bg-slate-900/60 hover:border-sky-500/50 hover:shadow-lg hover:shadow-sky-500/10'
							}`}
						>
							{isSelected && (
								<div className="absolute top-0 right-0 w-20 h-20 bg-sky-500/20 rounded-bl-full blur-2xl" />
							)}
							<button
								onClick={() => {
									handleToggleDataset(dataset);
									setShowPreview(false);
									setPreview(null);
								}}
								className="flex-1 p-6 text-left"
							>
								<div className="relative space-y-2">
									<div className="flex items-center gap-2">
										<div
											className={`w-3 h-3 rounded-full transition-all ${
												isSelected ? 'bg-sky-500' : 'bg-slate-600 group-hover:bg-sky-500/50'
											}`}
										/>
										<h3 className="font-semibold text-lg">{dataset.name}</h3>
									</div>
									<p className="text-xs text-slate-400 font-mono">{dataset.filename}</p>
								</div>
							</button>
							<div className="p-4 pt-0 border-t border-slate-800">
								<Dialog.Root
									open={showPreview && previewDataset?.id === dataset.id}
									onOpenChange={(open) => {
										if (!open) {
											setShowPreview(false);
											setPreviewDataset(null);
										}
									}}
								>
									<Dialog.Trigger asChild>
										<button
											onClick={(e) => {
												e.stopPropagation();
												fetchPreview(dataset);
											}}
											disabled={previewLoading && previewDataset?.id === dataset.id}
											className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg hover:border-sky-500 hover:text-sky-300 hover:bg-slate-700 transition-all text-sm disabled:opacity-50"
										>
											{previewLoading && previewDataset?.id === dataset.id ? 'Loading...' : 'Preview'}
										</button>
									</Dialog.Trigger>
								</Dialog.Root>
							</div>
						</div>
					);
				})}
			</div>

			{/* Preview Modal - Shared for all cards */}
			<Dialog.Root
				open={showPreview}
				onOpenChange={(open) => {
					if (!open) {
						setShowPreview(false);
						setPreviewDataset(null);
						setPreview(null);
					}
				}}
			>
				<Dialog.Portal>
					<Dialog.Overlay className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50" />
					<Dialog.Content className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-slate-900 border border-slate-700 rounded-2xl p-6 max-w-6xl w-[calc(100%-2rem)] h-[600px] max-h-[calc(100vh-2rem)] overflow-hidden z-50 shadow-2xl m-4">
						<div className="flex flex-col h-full">
							<div className="flex items-center justify-between mb-6 flex-shrink-0">
								<div>
									<Dialog.Title className="text-2xl font-bold">Dataset Preview</Dialog.Title>
									<Dialog.Description className="text-sm text-slate-400 mt-1">
										{previewDataset?.name || 'Dataset'}
									</Dialog.Description>
								</div>
								<div className="flex items-center gap-3">
									{preview && preview.preview.length < preview.total_rows && (
										<button
											onClick={() => previewDataset && fetchPreview(previewDataset, true)}
											disabled={previewLoading}
											className="text-xs px-3 py-1 bg-sky-600 hover:bg-sky-700 rounded-lg transition disabled:opacity-50"
										>
											{previewLoading ? 'Loading...' : 'Load Full'}
										</button>
									)}
									<Dialog.Close asChild>
										<button className="text-slate-400 hover:text-white transition p-2 rounded-lg hover:bg-slate-800">
											<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path
													strokeLinecap="round"
													strokeLinejoin="round"
													strokeWidth={2}
													d="M6 18L18 6M6 6l12 12"
												/>
											</svg>
										</button>
									</Dialog.Close>
								</div>
							</div>

							<div className="flex-1 flex flex-col space-y-4 overflow-hidden min-h-0">
								{previewLoading ? (
									<div className="flex-1 flex items-center justify-center text-slate-400">
										Loading preview...
									</div>
								) : preview ? (
									<>
										<div className="flex items-center gap-4 text-sm flex-shrink-0">
											<span className="text-slate-400">
												Showing <strong className="text-white">{preview.preview.length}</strong> of{' '}
												<strong className="text-white">{preview.total_rows}</strong> rows
											</span>
											<span className="text-slate-400">
												<strong className="text-white">{preview.total_columns}</strong> columns
											</span>
										</div>

										<div className="flex-1 overflow-y-auto overflow-x-auto border border-slate-700 rounded-lg min-h-0">
											<table className="w-full text-sm">
												<thead className="sticky top-0 bg-slate-800 z-10">
													<tr className="border-b border-slate-700">
														{preview.columns.map((col: string) => (
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
													{preview.preview.map((row: Record<string, unknown>, idx: number) => (
														<tr
															key={idx}
															className="border-b border-slate-800/50 hover:bg-slate-800/30"
														>
															{preview.columns.map((col: string) => (
																<td key={col} className="py-2 px-3">
																	<span className="font-mono text-xs">
																		{String(row[col] ?? '')}
																	</span>
																</td>
															))}
														</tr>
													))}
												</tbody>
											</table>
										</div>
									</>
								) : (
									<div className="flex-1 flex items-center justify-center text-slate-400">
										No preview available
									</div>
								)}
							</div>
						</div>
					</Dialog.Content>
				</Dialog.Portal>
			</Dialog.Root>

			{/* Fixed button at bottom */}
			<div className="fixed bottom-0 left-0 right-0 bg-slate-950/95 backdrop-blur-sm border-t border-slate-800 p-4 z-50">
				<div className="max-w-6xl mx-auto">
					<button
						onClick={handleSelect}
						disabled={selectedDatasets.size < 2}
						className="w-full px-6 py-4 bg-gradient-to-r from-sky-600 to-blue-600 hover:from-sky-700 hover:to-blue-700 rounded-xl font-semibold text-white shadow-lg shadow-sky-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none transform hover:scale-[1.02] active:scale-[0.98] disabled:transform-none"
					>
						{selectedDatasets.size < 2
							? `Select 2 Datasets (${selectedDatasets.size} selected)`
							: `Use ${selectedDatasets.size} Datasets (Will be merged)`}
					</button>
				</div>
			</div>
		</div>
	);
}
