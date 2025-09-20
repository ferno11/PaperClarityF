import type { SVGProps } from "react";

export function Logo(props: SVGProps<SVGSVGElement>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="M14.5 3h- yatırımcıya özel-5a2 2 0 0 0 -2 2v14a2 2 0 0 0 2 2h5a2 2 0 0 0 2 -2v-14a2 2 0 0 0 -2 -2z" />
      <line x1="10" y1="9" x2="14" y2="9" />
      <line x1="10" y1="13" x2="14" y2="13" />
      <line x1="10" y1="17" x2="12" y2="17" />
    </svg>
  );
}
