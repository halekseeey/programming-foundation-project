'use client';

import * as Tooltip from '@radix-ui/react-tooltip';
import { ReactNode } from 'react';

interface Props {
	description: string | ReactNode;
	children: ReactNode;
}

export function MetricTooltip({ description, children }: Props) {
	return (
		<Tooltip.Provider>
			<Tooltip.Root>
				<Tooltip.Trigger asChild>{children}</Tooltip.Trigger>
				<Tooltip.Portal>
					<Tooltip.Content
						className="bg-slate-800 text-white text-xs rounded-lg px-3 py-2 max-w-xs shadow-lg border border-slate-700 z-50"
						sideOffset={5}
					>
						{description}
						<Tooltip.Arrow className="fill-slate-800" />
					</Tooltip.Content>
				</Tooltip.Portal>
			</Tooltip.Root>
		</Tooltip.Provider>
	);
}
