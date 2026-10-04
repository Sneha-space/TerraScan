import { useCallback, useEffect, useRef, useState } from "react";
import { errorMessage } from "../api/client";

/**
 * Load data from one API call, with loading and error state.
 *
 *   const { data, loading, error, reload } = useApi(() => getStats(), []);
 *
 * deps work like useEffect's: the call runs again when they change.
 * reload({ quiet: true }) refreshes without showing the loading state.
 */
export default function useApi(request, deps) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const latest = useRef(0);

  const run = useCallback(request, deps);

  const reload = useCallback(
    async ({ quiet = false } = {}) => {
      const call = ++latest.current;
      if (!quiet) setLoading(true);
      setError(null);
      try {
        const res = await run();
        // a slower, older request must not overwrite a newer one
        if (call === latest.current) setData(res.data);
      } catch (err) {
        if (call === latest.current) setError(errorMessage(err));
      } finally {
        if (call === latest.current) setLoading(false);
      }
    },
    [run]
  );

  useEffect(() => {
    reload();
  }, [reload]);

  return { data, loading, error, reload };
}
