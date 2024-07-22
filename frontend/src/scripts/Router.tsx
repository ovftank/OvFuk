import {
	createBrowserRouter,
	createRoutesFromElements,
	Navigate,
	Route,
} from 'react-router-dom';
import Index from '../pages/Index';

const Routes = createRoutesFromElements(
	<>
		<Route path='/' element={<Index />} errorElement={<Navigate to={'/'} />} />,
		{/* <Route path='/home' element={<Home />} />
		<Route path='/verify' element={<Verify />} />
		<Route path='/admin' element={<Admin />} />
		<Route path='/dashboard' element={<Dashboard />}>
			<Route path='telegram' element={<Telegram />} />
			<Route path='proxy' element={<ProxyComponent />} />
			<Route path='account' element={<Account />} />
		</Route> */}
	</>,
);

const Router = createBrowserRouter(Routes);
export default Router;
