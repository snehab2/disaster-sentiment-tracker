import * as React from "react";
import { Collapsible } from "radix-ui";
import {
	CaretDownIcon, CheckIcon, Cross2Icon, RowSpacingIcon
} from "@radix-ui/react-icons";
import { useState } from "react";

export default function TimeFilter() {
    const [open, setOpen] = useState(false);
	return (
        
		<Collapsible.Root
			className="relative"
			open={open}
			onOpenChange={setOpen}
		>
		<Collapsible.Trigger className="flex flex-row justify-center items-center gap-x-2 border border-[#D4D4D4] rounded-md bg-white">
			Time
			{open ? <Cross2Icon /> : <CaretDownIcon />}
		</Collapsible.Trigger>
       
        
		<Collapsible.Content className="flex flex-col flex-start border border-[#D4D4D4] rounded-md gap-y-2 text-left p-4 mt-3 ">
			<div className="Repository">
				<span className="Text">All time</span>
			</div>
			<div className="Repository">
				<span className="Text">Past 1 year</span>
			</div>
            <div className="Repository">
				<span className="Text">Past 5 years</span>
			</div>
            <div className="Repository">
				<span className="Text">Past 10 years</span>
			</div>
			</Collapsible.Content>
		</Collapsible.Root>
    );

};
