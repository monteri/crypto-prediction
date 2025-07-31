import { useState } from 'react';

function Balance() {
  const [state, setState] = useState('100 000$');

  return (
    <div>
      <h1 style={{ color: "white" }}>My balans: {state}</h1>
    </div>
  );
}

export default Balance;