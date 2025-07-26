import { useParams } from 'react-router-dom';


function Coin() {
  const { id } = useParams();

  return (
    <div style={{ backgroundColor: "#222", height: "100vh", padding: "20px", color: 'white' }}>
      <h2>Coin Page 🪙</h2>
      <p>Selected coin ID: {id}</p>
    </div>
  );
}

export default Coin;