import type { ReactNode } from 'react';

const ART: ReactNode[] = [
  <>
    <path fill="#d8dfb8" d="M10 14q0-5 7-5h36q8 0 8 8v17q0 6-8 6H32L18 50l2-12q-10 0-10-7z" />
    <path fill="#faf7e8" d="M39 29h27q7 0 7 7v10q0 6-7 6h-2l2 8-14-8H42q-6 0-6-6V35q0-6 3-6z" />
    <path d="M21 22h25M21 29h14M46 39h16m-16 6h11" />
  </>,
  <>
    <circle fill="#f2dbaa" cx="38" cy="33" r="24" />
    <circle fill="#fffae8" cx="38" cy="33" r="19" />
    <path fill="#a8b38a" d="m49 19-7 19-15 10 8-20z" />
    <path d="m34 28 8 10M36 8V4h6v5M15 55l-6 5m50-43 7-5" />
  </>,
  <>
    <path fill="#d3dfcd" d="M6 19q15-7 32 2 14-10 32-6l4 33q-17-3-34 7-16-7-33-4z" />
    <path fill="#faf9ed" d="M8 15q15-6 30 4 13-10 29-8l3 31q-19 0-30 10-13-10-29-6z" />
    <path d="m38 19 2 33M16 23q9-2 16 3m-15 4q8-1 15 4m14-11 14-5m-13 12 15-5" />
    <path fill="#d7b562" d="m53 14 5-2 1 13-4-2-2 4z" />
  </>,
];

export const Doodle = ({ index }: { index: number }) => (
  <svg
    className="doodle" viewBox="0 0 82 64" fill="none" stroke="#42523b" strokeWidth="1.7"
    strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"
  >
    {ART[index]}
  </svg>
);
