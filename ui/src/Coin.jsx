import { useParams } from 'react-router-dom';


function Coin() {
  const { id } = useParams();

  return (
    <div className="app-container">
      <h2>Coin Page 🪙</h2>
      <p>Selected coin ID: {id}</p>
    </div>
  );
}

export default Coin;