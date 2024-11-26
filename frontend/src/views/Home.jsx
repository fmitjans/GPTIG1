import React, { useState, useEffect } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import data from '../assets/regiones_comunas.json';
import logo2 from '../assets/imagenmejorada2.png';
import { Link } from 'react-router-dom';
import '../styles/App.css';


export default function Home() {
  const [searchKeyword, setSearchKeyword] = useState('');
  const [region, setRegion] = useState('');
  const [nivelEducativo, setNivelEducativo] = useState('');
  const [jornadaLaboral, setJornadaLaboral] = useState('');
  const [fechaPublicacion, setFechaPublicacion] = useState('');
  const [buttonText, setButtonText] = useState('Buscar');
  const [jobs, setJobs] = useState([{
    empresa: 'Empresa Ejemplo',
    region: 'Región Ejemplo',
    nivelEducativo: 'Universitario',
    experiencia: '3 años',
    jornada: 'Full time',
    salario: 'CLP 1.500.000',
    cargo: 'Junior',
    titulo: 'Desarrollador Full Stack',
    descripcion: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam nec purus nec nunc ultricies ultricies. Nullam nec purus nec nunc ultricies ultricies.'
  }]);
  const [isLoading, setIsLoading] = useState(false); // Estado de carga añadido
  const [regiones, setRegiones] = useState([]);

  const nivelesEducativos = ['Sin educación formal', 'Educación básica incompleta', 'Educación básica completa', 
    'Educación media incompleta', 'Educación media completa', 'Educación técnica incompleta', 'Educación técnica completa', 
    'Educación universitaria incompleta', 'Educación universitaria completa', 'Magíster', 'Doctorado'];
  const jornadasLaborales = ['Full time', 'Part time'];
  const fechasPublicacion = ['', 'Hoy', 'Ayer', 'Menor a 3 días', 'Menor a 1 semana', 'Menor a 15 días', 'Menor a 1 mes', 'Menor a 2 meses'];

  useEffect(() => {
    setRegiones(Object.keys(data));
  }, []);

  const handleSearch = () => {
    const searchParams = {
      searchKeyword,
      region,
      nivelEducativo,
      jornadaLaboral,
      fechaPublicacion,
    };

    console.log(searchParams);

    setButtonText('Buscando...');
    setIsLoading(true); // Iniciar el estado de carga al hacer la búsqueda

    fetch(`http://localhost:8000/offers?keyword=${encodeURIComponent(JSON.stringify(searchParams))}`)
      .then(response => response.json())
      .then(data => {
        // console.log(data);
        const renamedJobs = data.map(job => ({
          empresa: job.datosEmpresaOferta,
          descripcion: job.descripcionOferta,
          titulo: job.tituloOferta,
          offerId: job.link.slice(26) // corregir esto. mandar solo id desde el backend
        }));
        setJobs(renamedJobs);
        console.log(renamedJobs);
      })
      .catch(error => {
        console.error('Error:', error);
      })
      .finally(() => {
        setIsLoading(false); // Terminar el estado de carga cuando la solicitud finalice
        setButtonText('Buscar');
      });

  };


  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="container mt-5">
      <h1 className="text-center mb-4">
        <img src={logo2} alt="Jobsmatch Logo" style={{ maxWidth: '600px', height: 'auto' }} />
      </h1>
      {/* Search bar row */}
      <div className="row mb-3 justify-content-center">
        <div className="col-md-10">
          <input
            type="text"
            className="form-control"
            placeholder="Profesión, empresa o palabra clave"
            value={searchKeyword}
            onChange={e => setSearchKeyword(e.target.value)}
            onKeyDown={handleKeyDown}
          />
        </div>
        <div className="col-md-2">
          <button className="custom-button" onClick={handleSearch} disabled={isLoading}>
            {buttonText}
          </button>
        </div>
      </div>

      {/* Filters form */}
      <div className="row mb-3">
        <div className="col-md-5">
          <select
            className="form-select"
            value={region}
            onChange={e => setRegion(e.target.value)}
            aria-label="Select Región"
          >
            <option value="">Región</option>
            {regiones.map((reg, index) => (
              <option key={index} value={reg}>
                {reg}
              </option>
            ))}
          </select>
        </div>
        <div className="col-md-5">
          <select
            className="form-select"
            value={nivelEducativo}
            onChange={e => setNivelEducativo(e.target.value)}
            aria-label="Select Nivel educativo"
          >
            <option value="">Nivel educativo</option>
            {nivelesEducativos.map((nivel, index) => (
              <option key={index} value={nivel}>
                {nivel}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="row mb-3">
        <div className="col-md-5">
          <select
            className="form-select"
            value={jornadaLaboral}
            onChange={e => setJornadaLaboral(e.target.value)}
            aria-label="Select Jornada laboral"
          >
            <option value="">Jornada laboral</option>
            {jornadasLaborales.map((jornada, index) => (
              <option key={index} value={jornada}>
                {jornada}
              </option>
            ))}
          </select>
        </div>
        <div className="col-md-5">
          <select
            className="form-select"
            value={fechaPublicacion}
            onChange={e => setFechaPublicacion(e.target.value)}
            aria-label="Select Fecha de publicación"
          >
            <option value="">Fecha de publicación</option>
            {fechasPublicacion.slice(1).map((fecha, index) => (
              <option key={index} value={fecha}>
                {fecha}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Muestra el estado de carga */}
      {isLoading ? (
        <div className="text-center">
          <div className="spinner"></div>
          <p>Cargando resultados...</p>          
        </div>
        ) : jobs.length === 0 ? (
          <div className="text-center mt-5">
            <h3>No se encontraron resultados</h3>
            <p>Intenta realizar una búsqueda con otros filtros o palabras clave.</p>
          </div>
        ) : (
        <div className="table-responsive mt-4">
          <table className="table table-bordered text-center">
            <thead className="table-light custom-table-header">
              <tr>
                <th>Titulo</th>
                <th>Empresa</th>
                <th>Descripcion</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((job, index) => (
                <tr key={index}>
                  <td>
                    <Link to={`/job/${job.offerId}`} style={{ textDecoration: 'none', color: '#007bff' }}>
                      {job.titulo}
                    </Link>
                  </td>
                  <td>{job.empresa}</td>
                  <td>{job.descripcion}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
