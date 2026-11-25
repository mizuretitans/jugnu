import { Route, Routes } from 'react-router';
import { RequireAuth } from './auth/RequireAuth';
import { Layout } from './components/Layout';
import { NotFound } from './components/Page';
import { AuthCallback } from './pages/AuthCallback';
import { Book } from './pages/Book';
import { Community } from './pages/Community';
import { ConversationPage } from './pages/Conversation';
import { DashboardPage } from './pages/Dashboard';
import { Guide } from './pages/Guide';
import { Home } from './pages/Home';
import { Login } from './pages/Login';
import { MentorProfile } from './pages/MentorProfile';
import { Mentors } from './pages/Mentors';
import { Welcome } from './pages/Welcome';

export function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="mentors" element={<Mentors />} />
        <Route path="mentors/:id" element={<MentorProfile />} />
        <Route path="mentors/:id/book" element={<RequireAuth role="student"><Book /></RequireAuth>} />
        <Route path="guide" element={<RequireAuth role="student"><Guide /></RequireAuth>} />
        <Route path="login" element={<Login />} />
        <Route path="auth/callback" element={<AuthCallback />} />
        <Route path="welcome" element={<Welcome />} />
        <Route path="dashboard" element={<RequireAuth><DashboardPage /></RequireAuth>} />
        <Route path="community/:field?" element={<Community />} />
        <Route path="messages/:requestId" element={<RequireAuth><ConversationPage /></RequireAuth>} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
