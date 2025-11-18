'use client';

import dynamic from 'next/dynamic';
import type { PlotlyFigure } from '@/lib/api';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface Props {
	data: PlotlyFigure;
	className?: string;
}

export function PlotlyChart({ data, className }: Props) {
	return (
		<div className={className}>
			<Plot data={data.data} layout={data.layout || {}} config={{ displayModeBar: false }} />
		</div>
	);
}
