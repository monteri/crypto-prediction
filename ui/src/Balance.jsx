import { useState } from 'react';

function Balance() {
  const [state, setState] = useState('100 000$');

  return (
    <div>
      <h1>My balans: {state}</h1>
    </div>
  );
}

export default Balance;