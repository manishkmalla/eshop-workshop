import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';

export default function FavouritesPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [favourites, setFavourites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: '/favourites' } });
      return;
    }

    api
      .getFavourites()
      .then(setFavourites)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [isAuthenticated, navigate]);

  async function handleRemove(productId) {
    setError('');
    try {
      await api.removeFavourite(productId);
      setFavourites((current) => current.filter((item) => item.id !== productId));
    } catch (err) {
      setError(err.message);
    }
  }

  if (loading) {
    return <p className="text-center text-slate-500">Loading favourites...</p>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Favourites</h1>
        <p className="mt-1 text-slate-500">Products you have saved for later, newest first.</p>
      </div>

      {error && <p className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}

      {favourites.length === 0 ? (
        <div className="card text-center">
          <p className="text-slate-500">No favourites yet</p>
          <Link to="/" className="btn-primary mt-4 inline-flex">
            Browse the catalog
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {favourites.map((item) => (
            <article key={item.id} className="card flex items-center gap-4">
              <img
                src={item.picture_uri}
                alt={item.name}
                className="h-20 w-20 rounded-lg bg-slate-100 object-cover"
              />
              <div className="flex-1">
                <p className="text-xs font-medium uppercase tracking-wide text-indigo-600">
                  {item.brand_name} · {item.type_name}
                </p>
                <h2 className="text-lg font-semibold text-slate-900">{item.name}</h2>
                <p className="text-sm text-slate-500 line-clamp-1">{item.description}</p>
              </div>
              <p className="text-xl font-bold text-slate-900">${item.price.toFixed(2)}</p>
              <button
                type="button"
                onClick={() => handleRemove(item.id)}
                className="btn-secondary"
                aria-label={`Remove ${item.name} from favourites`}
              >
                Remove
              </button>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
